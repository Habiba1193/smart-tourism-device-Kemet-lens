from pathlib import Path

from PySide6.QtGui import QFontDatabase


UI_FONT_STACK = '"Segoe UI", "Segoe UI Variable Text", Arial, sans-serif'
TITLE_FONT_STACK = '"Cinzel", Georgia, "Times New Roman", "Amiri", "Noto Naskh Arabic", "DecoType Naskh", serif'
ARABIC_FONT_STACK = '"Amiri", "Noto Naskh Arabic", "DecoType Naskh", "Segoe UI", sans-serif'
RESULT_LATIN_TITLE_FONT_STACK = '"Cormorant Garamond", Georgia, "Times New Roman", serif'
RESULT_LATIN_BODY_FONT_STACK = '"Source Sans 3", "Segoe UI Variable Text", "Segoe UI", Arial, sans-serif'

UI_FONT_FAMILY = "Segoe UI"
TITLE_FONT_FAMILY = "Cinzel"
TITLE_FALLBACK_FAMILY = "Georgia"
ARABIC_FONT_FAMILY = "DecoType Naskh"
RESULT_TITLE_FONT_FAMILY = "Cormorant Garamond"
RESULT_BODY_FONT_FAMILY = "Source Sans 3"


def load_app_fonts() -> None:
    """Register bundled/project fonts and useful Windows fallbacks."""
    project_fonts = Path(__file__).resolve().parent.parent / "assets" / "fonts"
    if project_fonts.exists():
        for path in project_fonts.glob("*.*"):
            if path.suffix.lower() in {".ttf", ".otf"}:
                QFontDatabase.addApplicationFont(str(path))

    font_dir = Path("C:/Windows/Fonts")
    for filename in [
        "segoeui.ttf",
        "segoeuib.ttf",
        "segoeuisb.ttf",
        "seguisb.ttf",
        "georgia.ttf",
        "georgiab.ttf",
        "georgiai.ttf",
        "seguisym.ttf",
        "times.ttf",
        "timesbd.ttf",
        "CormorantGaramond-Regular.ttf",
        "CormorantGaramond-SemiBold.ttf",
        "CormorantGaramond-Bold.ttf",
        "SourceSans3-Regular.ttf",
        "SourceSans3-SemiBold.ttf",
        "SourceSans3-Bold.ttf",
        "DTNASKH0.TTF",
        "DTNASKH1.TTF",
        "DTNASKH2.TTF",
        "DTNASKH3.TTF",
        "DTNASKH4.TTF",
    ]:
        path = font_dir / filename
        if path.exists():
            QFontDatabase.addApplicationFont(str(path))


def title_qfont_family() -> str:
    families = set(QFontDatabase.families())
    if TITLE_FONT_FAMILY in families:
        return TITLE_FONT_FAMILY
    return TITLE_FALLBACK_FAMILY


def result_title_qfont_family(language: str = "en") -> str:
    if language == "ar":
        return ARABIC_FONT_FAMILY
    families = set(QFontDatabase.families())
    if RESULT_TITLE_FONT_FAMILY in families:
        return RESULT_TITLE_FONT_FAMILY
    return TITLE_FALLBACK_FAMILY


def result_body_qfont_family(language: str = "en") -> str:
    if language == "ar":
        return ARABIC_FONT_FAMILY
    families = set(QFontDatabase.families())
    if RESULT_BODY_FONT_FAMILY in families:
        return RESULT_BODY_FONT_FAMILY
    return UI_FONT_FAMILY
