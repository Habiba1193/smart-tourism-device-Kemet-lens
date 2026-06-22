from .fonts import ARABIC_FONT_STACK, TITLE_FONT_STACK, UI_FONT_STACK


GOLD = "#e0ad3f"
GOLD_DARK = "#9a711f"
CREAM = "#ffe9ad"
PAPYRUS = "#f3dfae"
PAPYRUS_DARK_TEXT = "#2b2117"
INK = "#090c14"
INK_2 = "#10131d"
INK_3 = "#171923"
MUTED = "#b9a878"
BORDER = "#3a2d18"
GREEN = "#46c16d"


def app_qss(language: str = "en") -> str:
    body_font_stack = ARABIC_FONT_STACK if language == "ar" else UI_FONT_STACK
    return f"""
* {{
    font-family: {body_font_stack};
    letter-spacing: 0px;
}}

QWidget {{
    color: {CREAM};
}}

QScrollArea {{
    border: none;
    background: transparent;
}}

QScrollBar:vertical {{
    width: 4px;
    background: rgba(0, 0, 0, 35);
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: {GOLD};
    border-radius: 2px;
}}

QScrollBar:horizontal {{
    height: 0px;
    background: transparent;
}}

QLabel[role="brand"] {{
    color: {GOLD};
    font-family: {TITLE_FONT_STACK};
    font-size: 9px;
    letter-spacing: 4px;
}}

QLabel[role="title"] {{
    color: {CREAM};
    font-family: {TITLE_FONT_STACK};
    font-size: 23px;
    font-weight: 700;
}}

QLabel[role="section"] {{
    color: {CREAM};
    font-family: {TITLE_FONT_STACK};
    font-size: 17px;
    font-weight: 700;
}}

QLabel[role="subtitle"] {{
    color: {MUTED};
    font-size: 12px;
    line-height: 150%;
}}

QLabel[role="body"] {{
    color: #ddd3bd;
    font-size: 12px;
    line-height: 150%;
}}

QLabel[role="darkBody"] {{
    color: #2e281e;
    font-size: 12px;
    line-height: 145%;
}}

QLabel[role="tiny"] {{
    color: {MUTED};
    font-size: 9px;
}}

QPushButton {{
    border: none;
    padding: 0px 14px;
}}

QPushButton[variant="back"] {{
    color: {GOLD};
    background: transparent;
    font-size: 12px;
    text-align: left;
    padding: 0px;
}}

QPushButton[variant="primary"] {{
    background: {GOLD};
    color: #100d08;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 650;
    min-height: 52px;
}}

QPushButton[variant="primary"]:pressed {{
    background: #c89327;
}}

QPushButton[variant="secondary"] {{
    background: rgba(8, 10, 16, 205);
    color: {CREAM};
    border: 1px solid #2d2519;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    min-height: 48px;
}}

QPushButton[variant="tabOn"] {{
    background: {GOLD};
    color: #16100a;
    border-radius: 15px;
    min-height: 29px;
    font-size: 10px;
    font-weight: 700;
    padding: 0px 14px;
}}

QPushButton[variant="tabOff"] {{
    background: rgba(8, 10, 16, 220);
    color: {MUTED};
    border: 1px solid #272014;
    border-radius: 15px;
    min-height: 29px;
    font-size: 10px;
    font-weight: 650;
    padding: 0px 14px;
}}

QFrame[card="papyrus"] {{
    background: {PAPYRUS};
    border: 1px solid #f2d88e;
    border-radius: 14px;
}}

QFrame[card="dark"] {{
    background: rgba(8, 10, 16, 225);
    border: 1px solid #2b2317;
    border-radius: 14px;
}}

QFrame[card="glass"] {{
    background: rgba(31, 34, 45, 225);
    border: 1px solid rgba(255, 233, 173, 40);
    border-radius: 10px;
}}

QFrame[card="nav"] {{
    background: rgba(7, 9, 12, 242);
    border-top: 1px solid #201910;
}}

QFrame[card="fact"] {{
    background: {PAPYRUS};
    border: 1px solid #f3d889;
    border-radius: 10px;
}}
"""


APP_QSS = app_qss("en")
