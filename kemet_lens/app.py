from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QMainWindow, QStackedWidget, QWidget

from .data import ARTIFACTS, Artifact, normalize_artifact_key
from .detection import DemoDetector, Detection
from .screens.about import AboutScreen
from .screens.ask_bakkar import AskBakkarScreen
from .screens.detected_choice import DetectedChoiceScreen
from .screens.home import HomeScreen
from .screens.language import LanguageScreen
from .screens.processing import ProcessingScreen
from .screens.recent import RecentScreen
from .screens.result import ResultScreen
from .screens.scanner import ScannerScreen
from .screens.splash import SplashScreen
from .screens.unknown import UnknownScreen
from .theme import app_qss


class LaptopStage(QWidget):
    def __init__(self, stack: QStackedWidget, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.stack = stack

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.phone_frame = QFrame()
        self.phone_frame.setObjectName("phoneFrame")
        self.phone_frame.setFrameShape(QFrame.NoFrame)
        self.phone_frame.setStyleSheet("#phoneFrame { background: transparent; border: none; }")

        phone_layout = QHBoxLayout(self.phone_frame)
        phone_layout.setContentsMargins(0, 0, 0, 0)
        phone_layout.setSpacing(0)
        phone_layout.addWidget(stack)

        layout.addWidget(self.phone_frame)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self.phone_frame.setFixedSize(self.width(), self.height())

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        rect = self.rect()
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor("#000000"))
        gradient.setColorAt(0.48, QColor("#020306"))
        gradient.setColorAt(1.0, QColor("#080301"))
        painter.fillRect(rect, gradient)


class KemetLensWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Kemet Lens")
        self.setMinimumSize(900, 640)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.language = "en"
        self.detector = DemoDetector()

        self.pending_detection = Detection("tutankhamun", 0.93)
        self.pending_detections: list[Detection] = [self.pending_detection]

        self.current_artifact: Artifact = ARTIFACTS["tutankhamun"]
        self.current_confidence = self.current_artifact.default_confidence

        self.recent_keys: list[str] = []
        self.language_return_screen = "scanner"

        self.stack = QStackedWidget()
        self.stage = LaptopStage(self.stack)
        self.setCentralWidget(self.stage)

        exit_fullscreen = QAction("Exit Full Screen", self)
        exit_fullscreen.setShortcut("Esc")
        exit_fullscreen.triggered.connect(self.close)
        self.addAction(exit_fullscreen)

        self.screens = {
            "splash": SplashScreen(self),
            "home": HomeScreen(self),
            "language": LanguageScreen(self),
            "scanner": ScannerScreen(self),
            "processing": ProcessingScreen(self),
            "detected_choice": DetectedChoiceScreen(self),
            "result": ResultScreen(self),
            "ask_bakkar": AskBakkarScreen(self),
            "recent": RecentScreen(self),
            "unknown": UnknownScreen(self),
            "about": AboutScreen(self),
        }

        for screen in self.screens.values():
            self.stack.addWidget(screen)

        self.show_screen("splash")
        QTimer.singleShot(2800, lambda: self.show_screen("home"))

    def show_screen(self, name: str) -> None:
        screen = self.screens[name]

        if hasattr(screen, "refresh"):
            screen.refresh()

        if name == "scanner" and hasattr(screen, "set_object_detected"):
            screen.set_object_detected(False)

        self.stack.setCurrentWidget(screen)

    def set_language(self, language: str) -> None:
        self.language = language

        instance = QApplication.instance()
        if instance is not None:
            instance.setStyleSheet(app_qss(language))

        for screen in self.screens.values():
            if hasattr(screen, "refresh"):
                screen.refresh()

    def open_language(self, return_to: str = "scanner") -> None:
        self.language_return_screen = return_to
        self.show_screen("language")

    def continue_from_language(self) -> None:
        if self.language_return_screen == "result":
            self.screens["result"].set_artifact(self.current_artifact, self.current_confidence)
            self.show_screen("result")
            return

        if self.language_return_screen == "ask_bakkar":
            self.show_screen("ask_bakkar")
            return

        self.show_screen("scanner")

    def cancel_language(self) -> None:
        if self.language_return_screen == "result":
            self.show_screen("result")
            return

        if self.language_return_screen == "ask_bakkar":
            self.show_screen("ask_bakkar")
            return

        self.show_screen("home")

    def begin_demo_detection(self) -> None:
        self.pending_detection = self.detector.detect()
        self.pending_detections = [self.pending_detection]

        self.show_screen("processing")
        self.screens["processing"].start()

    def begin_demo_multi_detection(self) -> None:
        self.pending_detections = self.detector.detect_many()

        if self.pending_detections:
            self.pending_detection = self.pending_detections[0]

        self.show_screen("processing")
        self.screens["processing"].start()

    def simulate_unknown_detection(self) -> None:
        self.pending_detection = Detection("unknown_fragment", 0.21)
        self.pending_detections = [self.pending_detection]

        self.show_screen("processing")
        self.screens["processing"].start()

    def finish_processing(self) -> None:
        self.handle_detections(self.pending_detections)

    def handle_detection(self, class_name: str, confidence: float) -> None:
        self.handle_detections([Detection(class_name, confidence)])

    def handle_detections(self, detections) -> None:
        valid_detections = self._valid_detection_choices(detections)

        if not valid_detections:
            self.show_screen("unknown")
            return

        if len(valid_detections) == 1:
            key, confidence = valid_detections[0]
            self.choose_detected_artifact(key, confidence)
            return

        choice_screen = self.screens["detected_choice"]
        choice_screen.set_detections(valid_detections)
        self.show_screen("detected_choice")

    def choose_detected_artifact(self, key: str, confidence: int) -> None:
        self.current_artifact = ARTIFACTS[key]
        self.current_confidence = confidence

        self._remember(key)

        self.screens["result"].set_artifact(self.current_artifact, self.current_confidence)
        self.show_screen("result")

    def open_artifact(self, key: str) -> None:
        artifact = ARTIFACTS[key]

        self.current_artifact = artifact
        self.current_confidence = artifact.default_confidence

        self.screens["result"].set_artifact(artifact, artifact.default_confidence)
        self.show_screen("result")

    def _remember(self, key: str) -> None:
        self.recent_keys = [key] + [item for item in self.recent_keys if item != key]
        self.recent_keys = self.recent_keys[:5]

    def _valid_detection_choices(self, detections) -> list[tuple[str, int]]:
        """
        Convert raw detections into clean GUI choices.

        Rules:
        - Accept all 5 artifact classes.
        - Remove duplicate classes.
        - Keep the highest confidence for each class.
        - Hide weak detections below 50%.
        - Sort from highest confidence to lowest.
        """
        best: dict[str, int] = {}

        for detection in detections:
            class_name = ""
            confidence = 0.0

            if isinstance(detection, Detection):
                class_name = detection.class_name
                confidence = detection.confidence

            elif isinstance(detection, dict):
                class_name = str(
                    detection.get("class_name")
                    or detection.get("label")
                    or detection.get("name")
                    or ""
                )

                try:
                    confidence = float(detection.get("confidence", 0.0))
                except (TypeError, ValueError):
                    confidence = 0.0

            else:
                try:
                    class_name = str(detection[0])
                    confidence = float(detection[1])
                except (IndexError, TypeError, ValueError):
                    continue

            key = normalize_artifact_key(class_name)

            if key is None:
                continue

            if confidence < 0.50:
                continue

            confidence_percent = round(confidence * 100) if confidence <= 1 else round(confidence)

            if key not in best or confidence_percent > best[key]:
                best[key] = confidence_percent

        choices = sorted(best.items(), key=lambda item: item[1], reverse=True)

        return choices[:5]
