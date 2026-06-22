from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QImage, QKeySequence, QPainter, QPainterPath, QPixmap, QShortcut

from ..hde_hailo import HailoDetector
from ..theme import TITLE_FONT_STACK
from ..translations import text
from ..widgets import (
    GradientScreen,
    ScannerPreview,
    add_shadow,
    content_shell,
    make_button,
    role_label,
    spacer,
)


class LiveScannerPreview(ScannerPreview):
    def __init__(self) -> None:
        super().__init__()

        # Bigger camera preview for Raspberry Pi Touch Display 2 fullscreen layout.
        self.setFixedHeight(460)

        self.frame_pixmap = QPixmap()

    def set_frame(self, image: QImage) -> None:
        self.frame_pixmap = QPixmap.fromImage(image)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        if self.frame_pixmap.isNull():
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)

        path = QPainterPath()
        path.addRoundedRect(rect, 18, 18)
        painter.setClipPath(path)

        scaled = self.frame_pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation,
        )

        x = int((self.width() - scaled.width()) / 2)
        y = int((self.height() - scaled.height()) / 2)

        painter.drawPixmap(x, y, scaled)
        painter.fillRect(rect, QColor(2, 5, 10, 72))

        painter.setClipping(False)

        # Scanner frame corners.
        painter.setPen(QColor("#e0ad3f"))

        corner = 48
        pad = 22

        points = [
            ((pad, pad + corner), (pad, pad), (pad + corner, pad)),
            (
                (self.width() - pad - corner, pad),
                (self.width() - pad, pad),
                (self.width() - pad, pad + corner),
            ),
            (
                (pad, self.height() - pad - corner),
                (pad, self.height() - pad),
                (pad + corner, self.height() - pad),
            ),
            (
                (self.width() - pad - corner, self.height() - pad),
                (self.width() - pad, self.height() - pad),
                (self.width() - pad, self.height() - pad - corner),
            ),
        ]

        for a, b, c in points:
            painter.drawLine(*a, *b)
            painter.drawLine(*b, *c)

        self._draw_ai_lens_symbol(painter, self.width() / 2, self.height() / 2)

        y_line = self._line
        painter.fillRect(
            QRectF(24, y_line, self.width() - 48, 3),
            QColor(224, 173, 63, 118),
        )

        if self.object_detected:
            painter.setBrush(QColor(5, 8, 11, 232))
            painter.setPen(QColor("#20251d"))

            badge = QRectF(90, self.height() - 64, self.width() - 180, 40)
            painter.drawRoundedRect(badge, 20, 20)

            painter.setPen(QColor("#fff3cc"))
            painter.drawText(
                badge.adjusted(12, 0, -12, 0),
                Qt.AlignCenter,
                self.status_text,
            )


class ScannerScreen(GradientScreen):
    def __init__(self, app) -> None:
        super().__init__()

        self.app = app
        self.detector: HailoDetector | None = None
        self._starting = False

        # Prevent camera from restarting immediately after a successful detection.
        self.object_detected = False

        layout = content_shell((52, 62, 52, 38), 18)
        self.setLayout(layout)

        self.back = make_button("", "back", 32)
        self.back.clicked.connect(lambda: self.app.show_screen("language"))
        layout.addWidget(self.back)

        self.exit_button = make_button("Exit", "back", 32)
        self.exit_button.clicked.connect(self.app.close)
        layout.addWidget(self.exit_button)

        self.title = role_label("", "title")
        self.title.setStyleSheet(
            f"font-family: {TITLE_FONT_STACK}; "
            "font-size: 32px; "
            "font-weight: 800; "
            "color: #ffe9ad;"
        )
        layout.addWidget(self.title)

        self.subtitle = role_label("", "subtitle", True)
        self.subtitle.setStyleSheet(
            "font-size: 16px; "
            "font-weight: 650; "
            "color: #fff3cc;"
        )
        layout.addWidget(self.subtitle)

        layout.addSpacing(12)

        self.preview = LiveScannerPreview()
        layout.addWidget(self.preview)

        layout.addSpacing(18)

        self.capture = make_button("", "primary", 76)
        self.capture.clicked.connect(self.start_detection)
        self.capture.setStyleSheet(
            "font-size: 17px; "
            "font-weight: 800;"
        )
        add_shadow(self.capture)
        layout.addWidget(self.capture)

        layout.addWidget(spacer(14))
        layout.addStretch(1)

        shortcut = QShortcut(QKeySequence("U"), self)
        shortcut.activated.connect(self.app.simulate_unknown_detection)

        multi_shortcut = QShortcut(QKeySequence("M"), self)
        multi_shortcut.activated.connect(self.app.begin_demo_multi_detection)

        exit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        exit_shortcut.activated.connect(self.app.close)

        self.refresh()

    def refresh(self) -> None:
        language = self.app.language

        self.back.setText(f"←  {text(language, 'back')}")
        self.title.setText(text(language, "artifact_scanner"))
        self.subtitle.setText(text(language, "scanner_subtitle"))
        self.preview.set_status_text(text(language, "scanner_status"))
        self.preview.set_placeholder_text(text(language, "place_artifact_here"))
        self.capture.setText(text(language, "capture_artifact"))

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)

        # If detection already happened, do not restart camera automatically.
        if self.object_detected:
            return

        self.start_detection()

    def hideEvent(self, event) -> None:  # noqa: N802
        self.stop_detection()
        super().hideEvent(event)

    def start_detection(self) -> None:
        if self.object_detected:
            self.object_detected = False
            self.preview.set_object_detected(False)

        if self._starting:
            return

        if self.detector is not None and self.detector.isRunning():
            print("[SCANNER] Detector already running.", flush=True)
            return

        self._starting = True

        hef_path = self._hef_path()

        print(f"[SCANNER] Starting Hailo detector with HEF: {hef_path}", flush=True)

        self.capture.setEnabled(False)
        self.capture.setText("Starting camera...")

        self.detector = HailoDetector(
            hef_path,
            confidence_threshold=float(os.environ.get("HAILO_CONFIDENCE", "0.25")),
            stable_frames=int(os.environ.get("HAILO_STABLE_FRAMES", "3")),
        )

        self.detector.frame_ready.connect(self.set_frame)

        # Main signal for the new multiple-detection flow.
        self.detector.detections_ready.connect(self._artifacts_detected)

        # Do not connect detection_ready here because the updated Hailo detector
        # can also emit detections_ready. Connecting both may open screens twice.
        # self.detector.detection_ready.connect(self._artifact_detected)

        self.detector.debug_ready.connect(
            lambda message: print(f"[SCANNER] {message}", flush=True)
        )
        self.detector.error_ready.connect(self._detector_error)
        self.detector.finished.connect(self._detector_finished)
        self.detector.start()

    def stop_detection(self) -> None:
        if self.detector is not None and self.detector.isRunning():
            print("[SCANNER] Stopping detector...", flush=True)
            self.detector.stop()

    def set_object_detected(self, detected: bool) -> None:
        self.object_detected = detected
        self.preview.set_object_detected(detected)

    def set_frame(self, image: QImage) -> None:
        self.preview.set_frame(image)

        if self.capture.isEnabled() is False:
            self.capture.setEnabled(True)
            self.capture.setText(text(self.app.language, "capture_artifact"))

    def _artifact_detected(self, class_name: str, confidence: float) -> None:
        """
        Old single-detection handler kept for compatibility.
        The new flow mainly uses _artifacts_detected().
        """
        print(f"[SCANNER] Artifact detected: {class_name} ({confidence:.3f})", flush=True)

        self.object_detected = True
        self.preview.set_object_detected(True)

        self.stop_detection()
        self.app.handle_detection(class_name, confidence)

    def _artifacts_detected(self, detections: list) -> None:
        """
        New multiple-detection handler.

        It receives a list like:
        [
            {"class_name": "tut", "confidence": 0.91},
            {"class_name": "anubis", "confidence": 0.84},
        ]
        """
        print(f"[SCANNER] Multiple artifacts detected: {detections}", flush=True)

        self.object_detected = True
        self.preview.set_object_detected(True)

        self.stop_detection()
        self.app.handle_detections(detections)

    def _detector_error(self, message: str) -> None:
        print(f"[SCANNER][ERROR] {message}", flush=True)

        self._starting = False
        self.capture.setEnabled(True)
        self.capture.setText(text(self.app.language, "capture_artifact"))

    def _detector_finished(self) -> None:
        self._starting = False
        self.capture.setEnabled(True)
        self.capture.setText(text(self.app.language, "capture_artifact"))
        self.detector = None

    def _hef_path(self) -> Path:
        env_path = os.environ.get("HAILO_HEF_PATH")

        if env_path:
            return Path(env_path)

        project_root = Path(__file__).resolve().parents[2]

        return project_root / "models" / "smart_tourism_yolov8n_final_220calib_hailo8_no_nms.hef"
