from __future__ import annotations

import os
import sys

from PySide6.QtCore import qInstallMessageHandler
from PySide6.QtWidgets import QApplication

from kemet_lens.app import KemetLensWindow
from kemet_lens.fonts import load_app_fonts
from kemet_lens.theme import APP_QSS


def _qt_message_handler(mode, context, message: str) -> None:
    # The shipped theme contains a few selectors that some Qt builds warn about.
    # Keep the terminal useful on the Pi by hiding only this known noisy warning.
    if "Could not parse stylesheet" in message:
        return
    print(message, file=sys.stderr, flush=True)


def main() -> int:
    print("[KEMET] Starting Smart Tourism GUI...", flush=True)
    print(f"[KEMET] Python: {sys.executable}", flush=True)
    print(f"[KEMET] Working directory: {os.getcwd()}", flush=True)

    qInstallMessageHandler(_qt_message_handler)

    app = QApplication(sys.argv)
    load_app_fonts()
    app.setApplicationName("Kemet Lens")
    app.setStyleSheet(APP_QSS)

    window = KemetLensWindow()
    if os.environ.get("KEMET_WINDOWED", "0") == "1":
        print("[KEMET] Running windowed because KEMET_WINDOWED=1.", flush=True)
        window.resize(900, 720)
        window.show()
    else:
        print("[KEMET] Running fullscreen. Use the scanner Exit button or Ctrl+Q to close.", flush=True)
        window.showFullScreen()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
