import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kemet_lens.app import KemetLensWindow
from kemet_lens.data import TAB_NAMES
from kemet_lens.fonts import load_app_fonts
from kemet_lens.theme import APP_QSS


def main() -> int:
    out_dir = ROOT / "previews"
    out_dir.mkdir(exist_ok=True)

    app = QApplication([])
    load_app_fonts()
    app.setStyleSheet(APP_QSS)
    window = KemetLensWindow()

    for screen in ["splash", "home", "language", "scanner", "processing", "unknown", "recent", "about"]:
        window.show_screen(screen)
        app.processEvents()
        window.grab().save(str(out_dir / f"{screen}.png"))

    window.handle_detection("tutankhamun", 0.93)
    app.processEvents()
    window.grab().save(str(out_dir / "result_overview.png"))

    for tab in TAB_NAMES:
        window.show_screen("result")
        window.screens["result"].set_tab(tab)
        app.processEvents()
        name = tab.lower().replace(" ", "_").replace("?", "")
        window.grab().save(str(out_dir / f"result_{name}.png"))

    window.show_screen("ask_bakkar")
    app.processEvents()
    window.grab().save(str(out_dir / "ask_bakkar.png"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
