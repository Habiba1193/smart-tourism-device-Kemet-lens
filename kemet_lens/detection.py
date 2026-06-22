from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage


@dataclass
class Detection:
    class_name: str
    confidence: float


class DemoDetector:
    """Tiny local stand-in for a future model call."""

    def __init__(self) -> None:
        self._index = 0
        self._sequence = [
            Detection("anubis", 0.86),
            Detection("tutankhamun", 0.93),
            Detection("nefertiti", 0.88),
            Detection("pyramids", 0.91),
            Detection("ramses_ii", 0.89),
        ]
        self._multi_sequence = [
            [Detection("anubis", 0.86), Detection("tutankhamun", 0.93)],
            [Detection("nefertiti", 0.88), Detection("pyramids", 0.91), Detection("ramses_ii", 0.89)],
            [Detection("anubis", 0.84), Detection("ramses_ii", 0.89)],
        ]

    def detect(self) -> Detection:
        detection = self._sequence[self._index % len(self._sequence)]
        self._index += 1
        return detection

    def detect_many(self) -> list[Detection]:
        detections = self._multi_sequence[self._index % len(self._multi_sequence)]
        self._index += 1
        return list(detections)


class HailoDetector(QThread):
    frame_ready = Signal(QImage)
    detection_ready = Signal(str, float)
    error = Signal(str)

    def __init__(
        self,
        hef_path: str | Path | None = None,
        *,
        confidence_threshold: float = 0.65,
        stable_frames: int = 5,
        camera_size: tuple[int, int] = (640, 640),
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.hef_path = Path(
            hef_path
            or os.environ.get("HAILO_HEF_PATH", "")
            or Path(__file__).resolve().parents[1] / "models" / "smart_tourism_yolov8n_final_220calib_hailo8_with_nms.hef"
        )
        self.confidence_threshold = confidence_threshold
        self.stable_frames = stable_frames
        self.camera_size = camera_size
        self.labels = ["tutankhamun", "ramses_ii", "nefertiti", "anubis", "pyramids_of_giza"]
        self._running = False
        self._stable_label: str | None = None
        self._stable_count = 0

    def stop(self) -> None:
        self._running = False
        if self.isRunning():
            self.wait(2500)

    def run(self) -> None:
        self._running = True
        self._stable_label = None
        self._stable_count = 0

        try:
            camera = self._open_camera()
            hailo_context = self._open_hailo()
        except Exception as exc:  # noqa: BLE001
            self.error.emit(str(exc))
            self._running = False
            return

        try:
            with camera, hailo_context as infer:
                while self._running:
                    frame = camera.read()
                    if frame is None:
                        time.sleep(0.01)
                        continue

                    preview = self._to_qimage(frame)
                    if preview is not None:
                        self.frame_ready.emit(preview)

                    rgb_frame = self._ensure_rgb(frame)
                    input_frame = self._prepare_input(rgb_frame, infer.input_shape)
                    outputs = infer.infer(input_frame)
                    detection = self._best_detection(outputs)
                    if self._confirm_detection(detection):
                        assert detection is not None
                        self.detection_ready.emit(detection.class_name, detection.confidence)
                        self._running = False
                        break
        except Exception as exc:  # noqa: BLE001
            self.error.emit(str(exc))
        finally:
            self._running = False

    def _open_camera(self):
        try:
            from picamera2 import Picamera2

            return _PiCamera2Source(Picamera2(), self.camera_size)
        except Exception:
            try:
                import cv2

                return _OpenCVCameraSource(cv2.VideoCapture(0), self.camera_size)
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError("Could not open Raspberry Pi camera. Install picamera2 or opencv-python.") from exc

    def _open_hailo(self):
        if not self.hef_path.exists():
            raise FileNotFoundError(
                f"HEF model not found: {self.hef_path}. Set HAILO_HEF_PATH or place the HEF under project/models/."
            )
        return _HailoInfer(self.hef_path)

    def _prepare_input(self, frame: np.ndarray, input_shape: tuple[int, ...]) -> np.ndarray:
        height, width = self._input_hw(input_shape)
        try:
            import cv2

            resized = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
        except Exception:
            resized = np.resize(frame, (height, width, 3))
        return np.expand_dims(resized.astype(np.uint8), axis=0)

    @staticmethod
    def _input_hw(shape: tuple[int, ...]) -> tuple[int, int]:
        if len(shape) >= 4:
            return int(shape[1]), int(shape[2])
        if len(shape) >= 3:
            return int(shape[0]), int(shape[1])
        return 640, 640

    def _best_detection(self, outputs: Any) -> Detection | None:
        candidates: list[Detection] = []
        for tensor in self._flatten_outputs(outputs):
            candidates.extend(self._parse_tensor(tensor))
        candidates = [item for item in candidates if item.confidence >= self.confidence_threshold]
        if not candidates:
            return None
        return max(candidates, key=lambda item: item.confidence)

    def _flatten_outputs(self, outputs: Any) -> list[np.ndarray]:
        if isinstance(outputs, dict):
            values = outputs.values()
        elif isinstance(outputs, (list, tuple)):
            values = outputs
        else:
            values = [outputs]

        tensors: list[np.ndarray] = []
        for value in values:
            array = np.asarray(value)
            if array.dtype == object:
                for item in array.ravel():
                    tensors.extend(self._flatten_outputs(item))
            else:
                tensors.append(np.squeeze(array))
        return tensors

    def _parse_tensor(self, tensor: np.ndarray) -> list[Detection]:
        if tensor.size == 0:
            return []

        detections: list[Detection] = []

        # Hailo NMS often returns one tensor per class with rows like [y1, x1, y2, x2, score].
        if tensor.ndim == 3 and tensor.shape[-1] >= 5 and tensor.shape[0] == len(self.labels):
            for class_index, class_rows in enumerate(tensor):
                for row in np.reshape(class_rows, (-1, tensor.shape[-1])):
                    confidence = float(row[4])
                    if confidence > 0:
                        detections.append(Detection(self.labels[class_index], confidence))
            return detections

        rows = np.reshape(tensor, (-1, tensor.shape[-1])) if tensor.ndim > 1 else np.reshape(tensor, (1, -1))
        if rows.shape[-1] < 5:
            return []

        for row in rows:
            # Common decoded YOLO formats: [x1, y1, x2, y2, score, class] or [x, y, w, h, obj, class scores...].
            if rows.shape[-1] == 6:
                confidence = float(row[4])
                class_index = int(round(float(row[5])))
            else:
                objectness = float(row[4])
                class_scores = row[5:]
                if class_scores.size == 0:
                    continue
                class_index = int(np.argmax(class_scores))
                confidence = objectness * float(class_scores[class_index])

            if 0 <= class_index < len(self.labels):
                detections.append(Detection(self.labels[class_index], confidence))
        return detections

    def _confirm_detection(self, detection: Detection | None) -> bool:
        if detection is None:
            self._stable_label = None
            self._stable_count = 0
            return False
        if detection.class_name == self._stable_label:
            self._stable_count += 1
        else:
            self._stable_label = detection.class_name
            self._stable_count = 1
        return self._stable_count >= self.stable_frames

    @staticmethod
    def _ensure_rgb(frame: np.ndarray) -> np.ndarray:
        if frame.ndim == 2:
            return np.stack([frame, frame, frame], axis=-1)
        if frame.shape[-1] == 4:
            return frame[:, :, :3]
        return frame

    def _to_qimage(self, frame: np.ndarray) -> QImage | None:
        rgb = self._ensure_rgb(frame)
        if not rgb.flags["C_CONTIGUOUS"]:
            rgb = np.ascontiguousarray(rgb)
        height, width, channels = rgb.shape
        if channels != 3:
            return None
        return QImage(rgb.data, width, height, channels * width, QImage.Format_RGB888).copy()


class _PiCamera2Source:
    def __init__(self, camera, camera_size: tuple[int, int]) -> None:
        self.camera = camera
        self.camera_size = camera_size

    def __enter__(self):
        config = self.camera.create_preview_configuration(
            main={"size": self.camera_size, "format": "RGB888"}
        )
        self.camera.configure(config)
        self.camera.start()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.camera.stop()

    def read(self) -> np.ndarray | None:
        return self.camera.capture_array()


class _OpenCVCameraSource:
    def __init__(self, capture, camera_size: tuple[int, int]) -> None:
        self.capture = capture
        self.camera_size = camera_size

    def __enter__(self):
        if not self.capture.isOpened():
            raise RuntimeError("OpenCV camera index 0 is not available.")
        self.capture.set(3, self.camera_size[0])
        self.capture.set(4, self.camera_size[1])
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.capture.release()

    def read(self) -> np.ndarray | None:
        ok, frame = self.capture.read()
        if not ok:
            return None
        try:
            import cv2

            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception:
            return frame[:, :, ::-1]


class _HailoInfer:
    def __init__(self, hef_path: Path) -> None:
        self.hef_path = str(hef_path)
        self.input_shape: tuple[int, ...] = (1, 640, 640, 3)

    def __enter__(self):
        from hailo_platform import (
            ConfigureParams,
            FormatType,
            HEF,
            HailoStreamInterface,
            InferVStreams,
            InputVStreamParams,
            OutputVStreamParams,
            VDevice,
        )

        self._api = {
            "ConfigureParams": ConfigureParams,
            "FormatType": FormatType,
            "HEF": HEF,
            "HailoStreamInterface": HailoStreamInterface,
            "InferVStreams": InferVStreams,
            "InputVStreamParams": InputVStreamParams,
            "OutputVStreamParams": OutputVStreamParams,
            "VDevice": VDevice,
        }
        self.hef = HEF(self.hef_path)
        self.device = VDevice()
        configure_params = ConfigureParams.create_from_hef(self.hef, interface=HailoStreamInterface.PCIe)
        self.network_group = self.device.configure(self.hef, configure_params)[0]
        self.network_group_params = self.network_group.create_params()
        self.input_infos = self.hef.get_input_vstream_infos()
        self.output_infos = self.hef.get_output_vstream_infos()
        self.input_shape = tuple(self.input_infos[0].shape)
        self.input_name = self.input_infos[0].name
        self.input_params = InputVStreamParams.make_from_network_group(
            self.network_group, quantized=False, format_type=FormatType.UINT8
        )
        self.output_params = OutputVStreamParams.make_from_network_group(
            self.network_group, quantized=False, format_type=FormatType.FLOAT32
        )
        self.activation = self.network_group.activate(self.network_group_params)
        self.activation.__enter__()
        self.infer_pipeline = InferVStreams(self.network_group, self.input_params, self.output_params)
        self.infer_pipeline.__enter__()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.infer_pipeline.__exit__(exc_type, exc, traceback)
        self.activation.__exit__(exc_type, exc, traceback)
        if hasattr(self.device, "release"):
            self.device.release()
        elif hasattr(self.device, "close"):
            self.device.close()

    def infer(self, frame: np.ndarray) -> dict[str, np.ndarray]:
        return self.infer_pipeline.infer({self.input_name: frame})
