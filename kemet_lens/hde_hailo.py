from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage


# ============================================================
# YOLOv8n + Hailo no-NMS settings
# ============================================================

IMG_SIZE = 640
DEFAULT_CONF_THRES = 0.25
IOU_THRES = 0.45
REG_MAX = 16

# IMPORTANT:
# This must match the exact class order used during training/export.
# Your working live_no_nms_test.py uses this order.
CLASS_NAMES = ["tut", "ramsis", "nefertiti", "anubis", "pyramids"]


@dataclass
class HailoDetection:
    class_name: str
    confidence: float


# ============================================================
# YOLOv8 helper functions
# These are adapted from your working live_no_nms_test.py.
# ============================================================

def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-x))


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    x = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(x)
    return e / np.sum(e, axis=axis, keepdims=True)


def letterbox(
    image: np.ndarray,
    new_shape: int = IMG_SIZE,
    color: tuple[int, int, int] = (114, 114, 114),
) -> tuple[np.ndarray, float, int, int]:
    """
    Resize image without distortion.

    Why:
    YOLO was trained with square 640x640 input. A normal resize can stretch
    the artifact and make boxes inaccurate. Letterbox keeps the aspect ratio.
    """
    import cv2

    h, w = image.shape[:2]
    scale = min(new_shape / h, new_shape / w)

    new_w = int(round(w * scale))
    new_h = int(round(h * scale))

    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    canvas = np.full((new_shape, new_shape, 3), color, dtype=np.uint8)

    pad_x = (new_shape - new_w) // 2
    pad_y = (new_shape - new_h) // 2

    canvas[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = resized

    return canvas, scale, pad_x, pad_y


def fix_shape_to_hwc(arr: np.ndarray, h: int, w: int, c: int) -> np.ndarray:
    """
    Convert Hailo output tensor into HWC shape.

    Why:
    Hailo output shapes can appear as HWC, CHW, flat, or squeezed arrays.
    YOLO decoding needs each output as height x width x channels.
    """
    arr = np.squeeze(arr)

    if arr.shape == (h, w, c):
        return arr

    if arr.shape == (c, h, w):
        return np.transpose(arr, (1, 2, 0))

    if arr.shape == (h * w, c):
        return arr.reshape(h, w, c)

    if arr.size == h * w * c:
        return arr.reshape(h, w, c)

    raise ValueError(f"Cannot reshape output {arr.shape} to ({h}, {w}, {c})")


def decode_yolov8_outputs(
    outputs: dict[str, np.ndarray],
    conf_thres: float,
) -> tuple[list[list[float]], list[float], list[int]]:
    """
    Decode raw YOLOv8 no-NMS outputs from Hailo.

    Your model does not return ready final boxes.
    It returns raw YOLOv8 heads:
    - 80x80 bbox + class output
    - 40x40 bbox + class output
    - 20x20 bbox + class output

    This function converts them into:
    - boxes: [x1, y1, x2, y2]
    - scores
    - class IDs
    """
    decoded_boxes: list[list[float]] = []
    decoded_scores: list[float] = []
    decoded_classes: list[int] = []

    output_items = list(outputs.items())

    scales = [
        (80, 80, 8),
        (40, 40, 16),
        (20, 20, 32),
    ]

    bbox_outputs: dict[int, np.ndarray] = {}
    cls_outputs: dict[int, np.ndarray] = {}

    for name, value in output_items:
        arr = np.squeeze(value)
        size = arr.size

        if size == 80 * 80 * 64:
            bbox_outputs[80] = arr
        elif size == 80 * 80 * len(CLASS_NAMES):
            cls_outputs[80] = arr
        elif size == 40 * 40 * 64:
            bbox_outputs[40] = arr
        elif size == 40 * 40 * len(CLASS_NAMES):
            cls_outputs[40] = arr
        elif size == 20 * 20 * 64:
            bbox_outputs[20] = arr
        elif size == 20 * 20 * len(CLASS_NAMES):
            cls_outputs[20] = arr

    for h, w, stride in scales:
        if h not in bbox_outputs or h not in cls_outputs:
            continue

        bbox = fix_shape_to_hwc(bbox_outputs[h], h, w, 64).astype(np.float32)
        cls = fix_shape_to_hwc(cls_outputs[h], h, w, len(CLASS_NAMES)).astype(np.float32)

        # If class output is raw logits, convert it to probability.
        if cls.max() > 1.0 or cls.min() < 0.0:
            cls = sigmoid(cls)

        bbox = bbox.reshape(h, w, 4, REG_MAX)
        bbox_prob = softmax(bbox, axis=-1)

        bins = np.arange(REG_MAX, dtype=np.float32)
        dist = np.sum(bbox_prob * bins, axis=-1)

        for y in range(h):
            for x in range(w):
                class_scores = cls[y, x]
                class_id = int(np.argmax(class_scores))
                score = float(class_scores[class_id])

                if score < conf_thres:
                    continue

                l, t, r, b = dist[y, x]

                cx = (x + 0.5) * stride
                cy = (y + 0.5) * stride

                x1 = cx - l * stride
                y1 = cy - t * stride
                x2 = cx + r * stride
                y2 = cy + b * stride

                decoded_boxes.append([x1, y1, x2, y2])
                decoded_scores.append(score)
                decoded_classes.append(class_id)

    return decoded_boxes, decoded_scores, decoded_classes


def nms(
    boxes: list[list[float]],
    scores: list[float],
    classes: list[int],
    conf_thres: float,
    iou_thres: float = IOU_THRES,
) -> list[int]:
    """
    Apply class-wise Non-Maximum Suppression.

    Why:
    YOLO often outputs many overlapping boxes for the same artifact.
    NMS keeps the strongest box and removes duplicate boxes.
    """
    import cv2

    if len(boxes) == 0:
        return []

    boxes_np = np.array(boxes, dtype=np.float32)
    scores_np = np.array(scores, dtype=np.float32)
    classes_np = np.array(classes, dtype=np.int32)

    final_indices: list[int] = []

    for cls_id in np.unique(classes_np):
        idxs = np.where(classes_np == cls_id)[0]
        cls_boxes = boxes_np[idxs]
        cls_scores = scores_np[idxs]

        cv_boxes = []
        for b in cls_boxes:
            x1, y1, x2, y2 = b
            cv_boxes.append([float(x1), float(y1), float(x2 - x1), float(y2 - y1)])

        keep = cv2.dnn.NMSBoxes(
            cv_boxes,
            cls_scores.tolist(),
            conf_thres,
            iou_thres,
        )

        if len(keep) > 0:
            keep = np.array(keep).flatten()
            final_indices.extend(idxs[keep].tolist())

    return final_indices


# ============================================================
# GUI detector thread
# ============================================================

class HailoDetector(QThread):
    frame_ready = Signal(QImage)

    # Old signal kept for compatibility.
    # It sends only one artifact.
    detection_ready = Signal(str, float)

    # New signal.
    # It sends all detected artifacts as a list of dictionaries.
    detections_ready = Signal(list)

    debug_ready = Signal(str)
    error_ready = Signal(str)

    def __init__(
        self,
        hef_path: str | Path,
        *,
        confidence_threshold: float = DEFAULT_CONF_THRES,
        stable_frames: int = 3,
        camera_size: tuple[int, int] = (1280, 720),
        labels: list[str] | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.hef_path = Path(hef_path)
        self.confidence_threshold = confidence_threshold
        self.stable_frames = stable_frames
        self.camera_size = camera_size

        # Keep this equal to the model class names.
        self.labels = labels or CLASS_NAMES

        self._running = False

        # Old single-detection stability variable.
        self._stable_label: str | None = None

        # New multiple-detection stability variable.
        self._stable_signature = ""

        self._stable_count = 0

        # These are saved from letterbox preprocessing.
        self._last_scale = 1.0
        self._last_pad_x = 0
        self._last_pad_y = 0

    def stop(self) -> None:
        self._running = False
        if self.isRunning():
            self.wait(5000)

    def run(self) -> None:
        self._running = True
        self._stable_label = None
        self._stable_signature = ""
        self._stable_count = 0

        try:
            self._debug(f"Starting detector thread. HEF={self.hef_path}")
            camera = self._open_camera()
        except Exception as exc:
            self._error(str(exc))
            self._running = False
            return

        infer_context = None

        try:
            with camera:
                self._debug("Camera is ready. Live preview should now be visible.")

                infer = None
                try:
                    infer_context = self._open_hailo()
                    infer = infer_context.__enter__()
                    self._debug("Hailo model is ready. Detection is active.")
                except Exception as exc:
                    self._error(
                        f"Hailo detection disabled, but camera preview will continue. Reason: {exc}"
                    )

                while self._running:
                    frame = camera.read()

                    if frame is None:
                        time.sleep(0.02)
                        continue

                    qimage = self._to_qimage(frame)
                    if qimage is not None:
                        self.frame_ready.emit(qimage)

                    if infer is not None:
                        input_frame = self._prepare_input(frame, infer.input_shape)
                        outputs = infer.infer(input_frame)

                        detections = self._all_detections(outputs)

                        if self._is_stable_detection_snapshot(detections):
                            self._debug(
                                "Confirmed detections: "
                                + ", ".join(
                                    f"{d.class_name}={d.confidence:.3f}"
                                    for d in detections
                                )
                            )

                            payload = [
                                {
                                    "class_name": detection.class_name,
                                    "confidence": detection.confidence,
                                }
                                for detection in detections
                            ]

                            # New behavior: send all detected artifact choices.
                            self.detections_ready.emit(payload)

                            # Compatibility behavior:
                            # If other old code still listens to detection_ready,
                            # send the strongest one too only when there is one object.
                            if len(detections) == 1:
                                self.detection_ready.emit(
                                    detections[0].class_name,
                                    detections[0].confidence,
                                )

                            self._running = False
                            break

                if infer_context is not None:
                    infer_context.__exit__(None, None, None)

        except Exception as exc:
            self._error(str(exc))

        finally:
            self._running = False
            self._debug("Detector thread stopped.")

    def _open_camera(self):
        self._debug("Initializing Raspberry Pi camera...")

        try:
            from picamera2 import Picamera2

            self._debug("Using Picamera2.")
            return _PiCamera2Source(Picamera2(), self.camera_size)

        except Exception as picam_exc:
            raise RuntimeError(
                f"Could not open Picamera2 camera. Reason: {picam_exc}"
            ) from picam_exc

    def _open_hailo(self):
        self._debug("Loading Hailo runtime...")

        if not self.hef_path.exists():
            raise FileNotFoundError(f"HEF model not found: {self.hef_path}")

        return _HailoInfer(self.hef_path, self._debug)

    def _prepare_input(self, frame: np.ndarray, input_shape: tuple[int, ...]) -> np.ndarray:
        """
        Prepare camera frame for YOLOv8 Hailo model.

        Why:
        Your working standalone script uses:
        BGR/RGB frame -> letterbox 640 -> expand dims -> uint8.
        We keep the same logic here.
        """
        rgb = self._ensure_rgb(frame)

        resized, scale, pad_x, pad_y = letterbox(rgb, IMG_SIZE)

        self._last_scale = scale
        self._last_pad_x = pad_x
        self._last_pad_y = pad_y

        return np.expand_dims(resized.astype(np.uint8), axis=0)

    def _all_detections(self, outputs: Any) -> list[HailoDetection]:
        """
        Get all unique detected artifact classes from the raw Hailo output.

        Rules:
        - Run YOLO decoding.
        - Run NMS.
        - Keep all valid classes.
        - If the same class appears multiple times, keep the highest confidence.
        - Sort by confidence from highest to lowest.
        - Allow up to all 5 classes.
        """
        if not isinstance(outputs, dict):
            self._debug("Unexpected Hailo output type. Expected dict.")
            return []

        boxes, scores, classes = decode_yolov8_outputs(
            outputs,
            conf_thres=self.confidence_threshold,
        )

        keep = nms(
            boxes,
            scores,
            classes,
            conf_thres=self.confidence_threshold,
            iou_thres=IOU_THRES,
        )

        if not keep:
            return []

        best_by_class: dict[str, HailoDetection] = {}

        for idx in keep:
            class_id = int(classes[idx])
            confidence = float(scores[idx])

            if class_id < 0 or class_id >= len(self.labels):
                continue

            if confidence < self.confidence_threshold:
                continue

            class_name = self.labels[class_id]

            if (
                class_name not in best_by_class
                or confidence > best_by_class[class_name].confidence
            ):
                best_by_class[class_name] = HailoDetection(class_name, confidence)

        detections = list(best_by_class.values())
        detections.sort(key=lambda detection: detection.confidence, reverse=True)

        if detections:
            self._debug(
                "Detected candidates: "
                + ", ".join(
                    f"{d.class_name} confidence={d.confidence:.3f}"
                    for d in detections
                )
            )

        return detections[:5]

    def _best_detection(self, outputs: Any) -> HailoDetection | None:
        """
        Old helper kept for compatibility.

        It returns only the strongest detected artifact.
        The new app flow should use _all_detections instead.
        """
        detections = self._all_detections(outputs)

        if not detections:
            return None

        return detections[0]

    def _is_stable(self, detection: HailoDetection | None) -> bool:
        """
        Old single-artifact stability helper kept for compatibility.
        """
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

    def _is_stable_detection_snapshot(self, detections: list[HailoDetection]) -> bool:
        """
        Confirm multiple detections only after the same set of classes
        appears for several frames.

        Example:
        Frame 1: tut + anubis
        Frame 2: tut + anubis
        Frame 3: tut + anubis
        => stable, send both to GUI.

        This prevents the GUI from opening the choice screen because of
        one accidental frame.
        """
        if not detections:
            self._stable_signature = ""
            self._stable_label = None
            self._stable_count = 0
            return False

        signature = "|".join(sorted(detection.class_name for detection in detections))

        if signature == self._stable_signature:
            self._stable_count += 1
        else:
            self._stable_signature = signature
            self._stable_label = detections[0].class_name
            self._stable_count = 1

        return self._stable_count >= self.stable_frames

    @staticmethod
    def _ensure_rgb(frame: np.ndarray) -> np.ndarray:
        """
        Convert camera frame to correct RGB format for GUI and model input.
        """
        if frame.ndim == 2:
            return np.stack([frame, frame, frame], axis=-1)

        if frame.ndim == 3 and frame.shape[-1] == 4:
            bgr = frame[:, :, :3]
            return bgr[:, :, ::-1].copy()

        if frame.ndim == 3 and frame.shape[-1] == 3:
            return frame

        return frame

    def _to_qimage(self, frame: np.ndarray) -> QImage | None:
        """
        Convert NumPy frame to QImage so the GUI preview box can show it.
        """
        rgb = self._ensure_rgb(frame)

        if not rgb.flags["C_CONTIGUOUS"]:
            rgb = np.ascontiguousarray(rgb)

        if rgb.ndim != 3 or rgb.shape[-1] != 3:
            return None

        height, width, channels = rgb.shape

        return QImage(
            rgb.data,
            width,
            height,
            channels * width,
            QImage.Format_RGB888,
        ).copy()

    def _debug(self, message: str) -> None:
        print(f"[HDE-HAILO] {message}", flush=True)
        self.debug_ready.emit(message)

    def _error(self, message: str) -> None:
        print(f"[HDE-HAILO][ERROR] {message}", flush=True)
        self.error_ready.emit(message)


# ============================================================
# Camera sources
# ============================================================

class _PiCamera2Source:
    def __init__(self, camera, camera_size: tuple[int, int]) -> None:
        self.camera = camera
        self.camera_size = camera_size

    def __enter__(self):
        """
        Open Raspberry Pi camera.

        We use XRGB8888 because the GUI receives 4-channel frames from Picamera2.
        _ensure_rgb converts it to RGB.
        """
        config = self.camera.create_preview_configuration(
            main={
                "size": self.camera_size,
                "format": "XRGB8888",
            }
        )

        self.camera.configure(config)
        self.camera.start()

        # Give camera a moment to start.
        time.sleep(1)

        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        """
        Fully release the Raspberry Pi camera.

        This is important because if the camera is only stopped but not closed,
        Picamera2 can stay in Configured state and fail when the scanner starts again.
        """
        try:
            self.camera.stop()
        except Exception:
            pass

        try:
            self.camera.close()
        except Exception:
            pass

        time.sleep(0.5)

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
        try:
            self.capture.release()
        except Exception:
            pass

        time.sleep(0.2)

    def read(self) -> np.ndarray | None:
        ok, frame = self.capture.read()

        if not ok:
            return None

        try:
            import cv2

            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        except Exception:
            return frame[:, :, ::-1]


# ============================================================
# Hailo inference wrapper
# ============================================================

class _HailoInfer:
    def __init__(self, hef_path: Path, debug) -> None:
        self.hef_path = str(hef_path)
        self.debug = debug
        self.input_shape: tuple[int, ...] = (1, IMG_SIZE, IMG_SIZE, 3)

    def __enter__(self):
        """
        Initialize Hailo runtime.

        This uses the same Hailo API style as your working live_no_nms_test.py:
        - HEF(...)
        - VDevice()
        - ConfigureParams.create_from_hef(...)
        - InputVStreamParams.make(...)
        - OutputVStreamParams.make(...)
        - InferVStreams(...)
        """
        try:
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

        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "No module named 'hailo_platform'. Run this app with the Python environment "
                "that has the Hailo ARM64 SDK installed."
            ) from exc

        self.debug(f"Loading HEF model: {self.hef_path}")

        self.hef = HEF(self.hef_path)

        self.device = VDevice()

        configure_params = ConfigureParams.create_from_hef(
            self.hef,
            interface=HailoStreamInterface.PCIe,
        )

        network_groups = self.device.configure(self.hef, configure_params)
        self.network_group = network_groups[0]
        self.network_group_params = self.network_group.create_params()

        self.input_infos = self.hef.get_input_vstream_infos()
        self.output_infos = self.hef.get_output_vstream_infos()

        self.input_shape = tuple(self.input_infos[0].shape)
        self.input_name = self.input_infos[0].name

        self.debug(f"HEF input: {self.input_name}, shape={self.input_shape}")
        self.debug("HEF outputs: " + ", ".join(info.name for info in self.output_infos))

        # Important:
        # This matches your working script more closely than make_from_network_group.
        self.input_params = InputVStreamParams.make(
            self.network_group,
            format_type=FormatType.UINT8,
        )

        self.output_params = OutputVStreamParams.make(
            self.network_group,
            format_type=FormatType.FLOAT32,
        )

        self.activation = self.network_group.activate(self.network_group_params)
        self.activation.__enter__()

        self.pipeline = InferVStreams(
            self.network_group,
            self.input_params,
            self.output_params,
        )

        self.pipeline.__enter__()

        self.debug("Hailo inference pipeline is active.")

        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if hasattr(self, "pipeline"):
            self.pipeline.__exit__(exc_type, exc, traceback)

        if hasattr(self, "activation"):
            self.activation.__exit__(exc_type, exc, traceback)

        if hasattr(self, "device"):
            if hasattr(self.device, "release"):
                self.device.release()
            elif hasattr(self.device, "close"):
                self.device.close()

    def infer(self, frame: np.ndarray) -> dict[str, np.ndarray]:
        return self.pipeline.infer({self.input_name: frame})
