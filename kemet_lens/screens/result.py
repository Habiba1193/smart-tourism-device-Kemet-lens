from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QMouseEvent, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..data import Artifact, TAB_NAMES
from ..fonts import (
    ARABIC_FONT_STACK,
    RESULT_LATIN_BODY_FONT_STACK,
    RESULT_LATIN_TITLE_FONT_STACK,
    result_body_qfont_family,
    result_title_qfont_family,
)
from ..theme import CREAM, GOLD, MUTED, PAPYRUS_DARK_TEXT
from ..translations import artifact_text, tab_label, text
from ..widgets import (
    BottomNav,
    GradientScreen,
    RoundedImage,
    add_shadow,
    content_shell,
    make_button,
    role_label,
    transparent_scroll,
)


def _result_title_stack(language: str) -> str:
    return ARABIC_FONT_STACK if language == "ar" else RESULT_LATIN_TITLE_FONT_STACK


def _result_body_stack(language: str) -> str:
    return ARABIC_FONT_STACK if language == "ar" else RESULT_LATIN_BODY_FONT_STACK


class ResultTabBar(QWidget):
    tab_changed = Signal(str)
    offset_changed = Signal()

    def __init__(self, app, tabs: list[str]) -> None:
        super().__init__()

        self.app = app
        self.tabs = tabs
        self.active_tab = tabs[0]
        self.offset = 0
        self.drag_start_x: int | None = None
        self.drag_start_offset = 0

        self.setFixedHeight(58)
        self.setCursor(Qt.PointingHandCursor)

        self._rects: list[tuple[str, QRectF]] = []
        self._content_width = 0

    def set_offset(self, offset: int) -> None:
        self._set_offset(offset)

    def maximum_offset(self) -> int:
        self._measure_tabs()
        return max(0, self._content_width - max(1, self.width()))

    def set_active(self, tab: str) -> None:
        self.active_tab = tab
        self._ensure_visible(tab)
        self.update()

    def refresh_language(self) -> None:
        self._ensure_visible(self.active_tab)
        self.update()

    def wheelEvent(self, event) -> None:  # noqa: N802
        delta = event.angleDelta().x() or event.angleDelta().y()
        self._set_offset(self.offset - int(delta / 3))
        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self.drag_start_x = int(event.position().x())
            self.drag_start_offset = self.offset
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self.drag_start_x is not None:
            dx = int(event.position().x()) - self.drag_start_x
            self._set_offset(self.drag_start_offset - dx)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            moved = abs(int(event.position().x()) - (self.drag_start_x or int(event.position().x())))
            self._layout_tabs()

            if moved < 8:
                for tab, rect in self._rects:
                    if rect.contains(event.position()):
                        self.tab_changed.emit(tab)
                        break

            self.drag_start_x = None
            event.accept()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setFont(QFont(result_body_qfont_family(self.app.language), 13, QFont.Bold))
        metrics = QFontMetrics(painter.font())

        self._layout_tabs()

        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

        for tab, rect in self._rects:
            if rect.right() < 0 or rect.left() > self.width():
                continue

            selected = tab == self.active_tab

            path = QPainterPath()
            path.addRoundedRect(rect, 21, 21)

            painter.fillPath(path, QColor(GOLD if selected else "#090b10"))
            painter.setPen(QPen(QColor(GOLD), 1.3))
            painter.drawPath(path)

            painter.setPen(QColor("#14100a" if selected else MUTED))

            draw_rect = rect.adjusted(14, 0, -14, 0)
            painter.drawText(
                draw_rect,
                Qt.AlignCenter,
                metrics.elidedText(
                    tab_label(self.app.language, tab),
                    Qt.ElideRight,
                    int(draw_rect.width()),
                ),
            )

    def _ensure_visible(self, tab: str) -> None:
        widths = self._measure_tabs()
        x = 0

        for item, width in zip(self.tabs, widths):
            if item == tab:
                if x < self.offset:
                    self._set_offset(x - 12)
                elif x + width > self.offset + self.width():
                    self._set_offset(x + width - self.width() + 12)
                return

            x += width + 12

    def _measure_tabs(self) -> list[int]:
        metrics = QFontMetrics(QFont(result_body_qfont_family(self.app.language), 13, QFont.Bold))

        widths: list[int] = []
        total = 0

        for tab in self.tabs:
            label = tab_label(self.app.language, tab)
            width = max(112, metrics.horizontalAdvance(label) + 42)
            width = min(width, 230)
            widths.append(width)
            total += width + 12

        self._content_width = max(0, total - 12)

        return widths

    def _layout_tabs(self) -> None:
        widths = self._measure_tabs()
        maximum = self.maximum_offset()

        if self.offset > maximum:
            self.offset = maximum

        x = -self.offset
        self._rects.clear()

        for tab, width in zip(self.tabs, widths):
            rect = QRectF(x, 7, width, 42)
            self._rects.append((tab, rect))
            x += width + 12

    def _set_offset(self, offset: int, repaint: bool = True) -> None:
        maximum = self.maximum_offset()
        old_offset = self.offset
        self.offset = max(0, min(offset, maximum))

        if self.offset != old_offset:
            self.offset_changed.emit()

        if repaint:
            self.update()


class TabScrollIndicator(QWidget):
    def __init__(self, tab_bar: ResultTabBar) -> None:
        super().__init__()

        self.tab_bar = tab_bar
        self.setFixedHeight(16)
        self.setCursor(Qt.PointingHandCursor)

        self.drag_start_x: int | None = None
        self.drag_start_offset = 0

        tab_bar.offset_changed.connect(self.update)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        track = self._track_rect()

        track_path = QPainterPath()
        track_path.addRoundedRect(track, 4.5, 4.5)
        painter.fillPath(track_path, QColor("#070e1b"))

        thumb = self._thumb_rect()

        thumb_path = QPainterPath()
        thumb_path.addRoundedRect(thumb, 4.5, 4.5)
        painter.fillPath(thumb_path, QColor(GOLD))

    def wheelEvent(self, event) -> None:  # noqa: N802
        delta = event.angleDelta().x() or event.angleDelta().y()
        self.tab_bar.set_offset(self.tab_bar.offset - int(delta / 3))
        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
            self.drag_start_x = int(event.position().x())
            self.drag_start_offset = self.tab_bar.offset

            if not self._thumb_rect().contains(event.position()):
                self._jump_to(event.position().x())

            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self.drag_start_x is not None:
            thumb = self._thumb_rect()
            track = self._track_rect()
            available = max(1, int(track.width() - thumb.width()))
            maximum = self.tab_bar.maximum_offset()
            dx = int(event.position().x()) - self.drag_start_x
            self.tab_bar.set_offset(self.drag_start_offset + int(dx * maximum / available))
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self.drag_start_x = None
            self.setCursor(Qt.PointingHandCursor)
            event.accept()

    def _jump_to(self, x: float) -> None:
        thumb = self._thumb_rect()
        track = self._track_rect()
        available = max(1, int(track.width() - thumb.width()))
        maximum = self.tab_bar.maximum_offset()
        target = int((x - track.left() - thumb.width() / 2) * maximum / available)
        self.tab_bar.set_offset(target)

    def _track_rect(self) -> QRectF:
        return QRectF(0, 4, self.width(), 9)

    def _thumb_rect(self) -> QRectF:
        self.tab_bar._measure_tabs()

        track = self._track_rect()
        content_width = max(self.tab_bar._content_width, self.tab_bar.width(), 1)
        viewport_width = max(self.tab_bar.width(), 1)

        if content_width <= viewport_width:
            thumb_width = max(110, int(track.width() * 0.42))
            thumb_x = 0
        else:
            thumb_width = max(82, int(track.width() * viewport_width / content_width))
            max_offset = max(1, content_width - viewport_width)
            thumb_x = int((track.width() - thumb_width) * self.tab_bar.offset / max_offset)

        return QRectF(track.left() + thumb_x, track.top(), thumb_width, track.height())


class ResultBadgeIcon(QWidget):
    def __init__(self, kind: str) -> None:
        super().__init__()

        self.kind = kind
        self.setFixedSize(42, 42)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(224, 173, 63, 45))
        painter.drawEllipse(QRectF(0.5, 0.5, 41, 41))

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(GOLD), 2.15, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        if self.kind == "book":
            left_page = QPainterPath()
            left_page.moveTo(8, 12)
            left_page.cubicTo(12, 10.5, 16, 11.2, 21, 15)
            left_page.lineTo(21, 31)
            left_page.cubicTo(16, 27.5, 12, 27, 8, 28)
            left_page.closeSubpath()

            right_page = QPainterPath()
            right_page.moveTo(34, 12)
            right_page.cubicTo(30, 10.5, 26, 11.2, 21, 15)
            right_page.lineTo(21, 31)
            right_page.cubicTo(26, 27.5, 30, 27, 34, 28)
            right_page.closeSubpath()

            painter.drawPath(left_page)
            painter.drawPath(right_page)
            painter.drawLine(21, 15, 21, 31)
            painter.drawLine(12, 18, 18, 19)
            painter.drawLine(24, 19, 30, 18)

        elif self.kind == "temple":
            painter.drawLine(10, 32, 32, 32)
            painter.drawLine(12, 26, 30, 26)
            painter.drawLine(15, 26, 15, 15)
            painter.drawLine(21, 26, 21, 15)
            painter.drawLine(27, 26, 27, 15)

            roof = QPainterPath()
            roof.moveTo(9, 15)
            roof.lineTo(21, 8)
            roof.lineTo(33, 15)
            roof.closeSubpath()
            painter.drawPath(roof)

        elif self.kind == "checklist":
            painter.drawRoundedRect(QRectF(12, 9, 18, 23), 3, 3)
            painter.drawLine(15, 16, 17, 18)
            painter.drawLine(17, 18, 21, 13.5)
            painter.drawLine(23, 16, 28, 16)
            painter.drawLine(15, 24, 17, 26)
            painter.drawLine(17, 26, 21, 21.5)
            painter.drawLine(23, 24, 28, 24)

        elif self.kind == "timeline":
            painter.drawLine(14, 9, 14, 32)

            for y in (10, 21, 31):
                painter.setBrush(QColor(GOLD))
                painter.drawEllipse(QRectF(11.5, y - 2.5, 5, 5))
                painter.setBrush(Qt.NoBrush)
                painter.drawLine(18, y, 31, y)

        elif self.kind == "star":
            star = QPainterPath()
            star.moveTo(21, 8)
            star.lineTo(24, 17)
            star.lineTo(34, 17)
            star.lineTo(26.2, 22.5)
            star.lineTo(29, 32)
            star.lineTo(21, 26.5)
            star.lineTo(13, 32)
            star.lineTo(15.8, 22.5)
            star.lineTo(8, 17)
            star.lineTo(18, 17)
            star.closeSubpath()
            painter.drawPath(star)

        elif self.kind == "question":
            painter.setFont(QFont(result_title_qfont_family(), 24, QFont.Bold))
            painter.drawText(QRectF(0, 3, 42, 36), Qt.AlignCenter, "?")

        elif self.kind == "eye":
            eye = QPainterPath()
            eye.moveTo(8, 21)
            eye.cubicTo(14, 12, 28, 12, 34, 21)
            eye.cubicTo(28, 29, 14, 29, 8, 21)
            painter.drawPath(eye)
            painter.drawEllipse(QRectF(16, 17, 10, 10))
            painter.drawLine(27, 28, 33, 34)
            painter.drawLine(19, 29, 15, 35)

        elif self.kind == "sparkle":
            def sparkle_path(cx: float, cy: float, outer: float, inner: float) -> QPainterPath:
                path = QPainterPath()
                path.moveTo(cx, cy - outer)
                path.lineTo(cx + inner, cy - inner)
                path.lineTo(cx + outer, cy)
                path.lineTo(cx + inner, cy + inner)
                path.lineTo(cx, cy + outer)
                path.lineTo(cx - inner, cy + inner)
                path.lineTo(cx - outer, cy)
                path.lineTo(cx - inner, cy - inner)
                path.closeSubpath()
                return path

            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(GOLD))
            painter.drawPath(sparkle_path(21, 19, 11, 3.4))
            painter.drawPath(sparkle_path(11, 12, 4.6, 1.5))
            painter.drawPath(sparkle_path(31, 31, 4.8, 1.6))


class ResultScreen(GradientScreen):
    def __init__(self, app) -> None:
        super().__init__()

        self.app = app
        self.artifact: Artifact = app.current_artifact
        self.confidence = app.current_confidence
        self.active_tab = "Overview"
        self.localized = artifact_text(self.app.language, self.artifact)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        top = QWidget()
        top_layout = content_shell((52, 54, 52, 0), 18)
        top.setLayout(top_layout)
        outer.addWidget(top)

        self.back = make_button("", "back", 32)
        self.back.clicked.connect(lambda: self.app.show_screen("scanner"))
        top_layout.addWidget(self.back)

        self.title = role_label("", "title")
        top_layout.addWidget(self.title)

        self.profile_card = QFrame()
        self.profile_card.setProperty("card", "papyrus")
        self.profile_card.setFixedHeight(455)
        add_shadow(self.profile_card, 26, 70)

        profile_layout = QVBoxLayout(self.profile_card)
        profile_layout.setContentsMargins(0, 0, 0, 0)
        profile_layout.setSpacing(0)

        self.image_wrap = QFrame()
        self.image_wrap.setFixedHeight(300)

        image_layout = QVBoxLayout(self.image_wrap)
        image_layout.setContentsMargins(0, 0, 0, 0)

        self.image = RoundedImage(self.artifact.image, radius=16)
        image_layout.addWidget(self.image)

        self.badge = QLabel()
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setFixedSize(140, 40)
        self.badge.setStyleSheet(
            f"background: {GOLD}; "
            "color: #16100a; "
            "border-radius: 20px; "
            "font-size: 13px; "
            "font-weight: 900;"
        )
        self.badge.setParent(self.image_wrap)
        self.badge.hide()

        profile_layout.addWidget(self.image_wrap)

        text_area = QFrame()
        text_area.setStyleSheet("background: transparent;")

        text_layout = QVBoxLayout(text_area)
        text_layout.setContentsMargins(24, 16, 24, 18)
        text_layout.setSpacing(8)

        self.name = QLabel()
        self.description = QLabel()
        self.description.setWordWrap(True)

        text_layout.addWidget(self.name)
        text_layout.addWidget(self.description, 1)

        profile_layout.addWidget(text_area, 1)

        top_layout.addWidget(self.profile_card)

        self.tab_bar = ResultTabBar(self.app, TAB_NAMES)
        self.tab_bar.tab_changed.connect(self.set_tab)
        top_layout.addWidget(self.tab_bar)

        self.tab_indicator = TabScrollIndicator(self.tab_bar)
        top_layout.addWidget(self.tab_indicator)

        self.content_host = QWidget()
        self.content_layout = QVBoxLayout(self.content_host)
        self.content_layout.setContentsMargins(52, 18, 52, 24)
        self.content_layout.setSpacing(16)

        outer.addWidget(transparent_scroll(self.content_host), 1)

        self.nav = BottomNav(
            lambda: self.app.show_screen("scanner"),
            lambda: self.app.show_screen("home"),
            lambda: self.app.show_screen("ask_bakkar"),
            lambda: self.app.open_language("result"),
            lambda: self.app.show_screen("recent"),
            self.app.language,
            use_bakkar_image=True,
        )
        outer.addWidget(self.nav)

        self._apply_result_fonts()
        self.set_artifact(self.artifact, self.confidence)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)

        if hasattr(self, "badge"):
            self._position_badge()

    def set_artifact(self, artifact: Artifact, confidence: int) -> None:
        self.artifact = artifact
        self.confidence = confidence
        self.localized = artifact_text(self.app.language, artifact)

        self.image.set_image(artifact.image)

        self.name.setText(self.localized["display_name"].upper())
        self.description.setText(self.localized["short_description"])

        badge_text = text(self.app.language, "match_badge", confidence=confidence)
        self.badge.setText(badge_text)

        badge_width = min(210, max(140, self.badge.fontMetrics().horizontalAdvance(badge_text) + 40))
        self.badge.setFixedSize(badge_width, 40)

        self.image.set_badge_text(badge_text)

        self._position_badge()
        self.set_tab("Overview")

    def _position_badge(self) -> None:
        self.badge.move(max(0, self.image_wrap.width() - self.badge.width() - 22), 16)
        self.badge.raise_()

    def refresh(self) -> None:
        self._apply_result_fonts()

        self.back.setText(f"←  {text(self.app.language, 'back')}")
        self.title.setText(text(self.app.language, "artifact_profile"))

        self.nav.set_language(self.app.language)
        self.tab_bar.refresh_language()
        self.tab_indicator.update()

        self.set_artifact(self.app.current_artifact, self.app.current_confidence)

    def _apply_result_fonts(self) -> None:
        title_stack = _result_title_stack(self.app.language)
        body_stack = _result_body_stack(self.app.language)

        self.title.setStyleSheet(
            f"font-family: {title_stack}; "
            "font-size: 32px; "
            "font-weight: 900; "
            "color: #ffe9ad;"
        )

        self.name.setStyleSheet(
            f"color: {PAPYRUS_DARK_TEXT}; "
            f"font-family: {title_stack}; "
            "font-size: 32px; "
            "font-weight: 900;"
        )

        self.description.setStyleSheet(
            f"color: #67583d; "
            f"font-family: {body_stack}; "
            "font-size: 16px; "
            "font-weight: 650; "
            "line-height: 150%;"
        )

    def set_tab(self, tab: str) -> None:
        self.active_tab = tab
        self.tab_bar.set_active(tab)
        self._render_content()

    def _clear_content(self) -> None:
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()

    def _render_content(self) -> None:
        self._clear_content()

        if self.active_tab == "Quick Facts":
            self._render_facts()
        elif self.active_tab == "Historical Timeline":
            self._render_timeline()
        else:
            text_value = {
                "Overview": self.localized["overview"],
                "History": self.localized["history"],
                "Why It Matters": self.localized["why"],
                "Did You Know?": self.localized.get("did_you_know_text", self.localized["did_you_know"]),
                "Hidden Info": self.localized.get("hidden_info_text", self.localized["hidden_info"]),
                "Fun Facts": self.localized.get("fun_facts_text", self.localized["fun_facts"]),
            }[self.active_tab]

            self._render_text_cards(self.active_tab, text_value)

        self.content_layout.addStretch(1)

    def _tab_icon_kind(self, tab: str) -> str:
        return {
            "Overview": "book",
            "History": "temple",
            "Quick Facts": "checklist",
            "Historical Timeline": "timeline",
            "Why It Matters": "star",
            "Did You Know?": "question",
            "Hidden Info": "eye",
            "Fun Facts": "sparkle",
        }.get(tab, "scroll")

    def _section_header(self, tab: str) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)

        badge = ResultBadgeIcon(self._tab_icon_kind(tab))
        row.addWidget(badge)

        heading = QLabel(tab_label(self.app.language, tab).upper())
        heading.setStyleSheet(
            f"color: {CREAM}; "
            f"font-family: {_result_title_stack(self.app.language)}; "
            "font-size: 22px; "
            "font-weight: 800;"
        )
        row.addWidget(heading, 1)

        return row

    def _render_text_cards(self, tab: str, text: str) -> None:
        blocks = [block.strip() for block in text.split("\n\n") if block.strip()]

        self.content_layout.addWidget(self._section_title_card(tab))

        if not blocks:
            self.content_layout.addWidget(self._dark_text_card(tab, text))
            return

        index = 0

        while index < len(blocks):
            title = ""
            body = blocks[index]

            if self._looks_like_subtitle(body) and index + 1 < len(blocks):
                title = body
                body = blocks[index + 1]
                index += 2
            else:
                index += 1

            self.content_layout.addWidget(self._dark_text_card(tab, body, title))

    def _section_title_card(self, tab: str) -> QFrame:
        card = QFrame()
        card.setProperty("card", "dark")
        card.setMinimumHeight(82)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 16, 22, 16)
        layout.addLayout(self._section_header(tab))

        return card

    @staticmethod
    def _looks_like_subtitle(block: str) -> bool:
        lines = block.splitlines()

        if len(lines) != 1:
            return False

        text_value = lines[0].strip()

        if not text_value or len(text_value) > 72:
            return False

        return text_value[-1] not in ".!?:;"

    def _dark_text_card(self, tab: str, text: str, title: str = "") -> QFrame:
        card = QFrame()
        card.setProperty("card", "dark")
        card.setMinimumHeight(120)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(9)

        if title:
            title_label = QLabel(title.upper())
            title_label.setWordWrap(True)
            title_label.setStyleSheet(
                f"color: {GOLD}; "
                f"font-family: {_result_title_stack(self.app.language)}; "
                "font-size: 18px; "
                "font-weight: 800;"
            )
            layout.addWidget(title_label)

        body = QLabel(text)
        body.setWordWrap(True)
        body.setStyleSheet(
            f"color: #e7dfcf; "
            f"font-family: {_result_body_stack(self.app.language)}; "
            "font-size: 16px; "
            "font-weight: 500; "
            "line-height: 155%;"
        )
        layout.addWidget(body)

        return card

    def _render_facts(self) -> None:
        header_card = QFrame()
        header_card.setProperty("card", "dark")
        header_card.setMinimumHeight(82)

        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(22, 16, 22, 16)
        header_layout.addLayout(self._section_header("Quick Facts"))

        self.content_layout.addWidget(header_card)

        grid_host = QWidget()
        grid = QGridLayout(grid_host)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)

        facts = self.localized.get("quick_facts_pairs", self.localized["quick_facts"])

        for index, (label, value) in enumerate(facts):
            fact = QFrame()
            fact.setProperty("card", "fact")
            fact.setMinimumHeight(110)

            box = QVBoxLayout(fact)
            box.setContentsMargins(18, 14, 18, 14)
            box.setSpacing(6)

            value_widget = QLabel(value)
            value_widget.setWordWrap(True)
            value_widget.setStyleSheet(
                f"color: {PAPYRUS_DARK_TEXT}; "
                f"font-family: {_result_body_stack(self.app.language)}; "
                "font-size: 16px; "
                "font-weight: 650;"
            )

            if label:
                label_widget = QLabel(label.upper())
                label_widget.setStyleSheet(
                    f"color: #8f7a50; "
                    f"font-family: {_result_body_stack(self.app.language)}; "
                    "font-size: 12px; "
                    "font-weight: 800;"
                )
                box.addWidget(label_widget)

            box.addWidget(value_widget)

            grid.addWidget(fact, index // 2, index % 2)

        self.content_layout.addWidget(grid_host)

    def _render_timeline(self) -> None:
        card = QFrame()
        card.setProperty("card", "dark")
        card.setMinimumHeight(250)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(12)

        layout.addLayout(self._section_header("Historical Timeline"))

        timeline = self.localized.get("timeline_pairs", self.localized["timeline"])

        for date, item in timeline:
            row = QHBoxLayout()
            row.setSpacing(12)

            dot_col = QVBoxLayout()

            dot = QLabel("●")
            dot.setStyleSheet(
                f"color: {GOLD}; "
                "font-size: 15px;"
            )
            dot_col.addWidget(dot, 0, Qt.AlignTop | Qt.AlignHCenter)

            line = QFrame()
            line.setFixedWidth(2)
            line.setStyleSheet("background: rgba(224, 173, 63, 65);")
            dot_col.addWidget(line, 1, Qt.AlignHCenter)

            row.addLayout(dot_col)

            text_box = QVBoxLayout()
            text_box.setSpacing(4)

            date_label = QLabel(date)
            date_label.setStyleSheet(
                f"color: {GOLD}; "
                f"font-family: {_result_body_stack(self.app.language)}; "
                "font-size: 16px; "
                "font-weight: 800;"
            )

            body = QLabel(item)
            body.setWordWrap(True)
            body.setStyleSheet(
                f"color: #e7dfcf; "
                f"font-family: {_result_body_stack(self.app.language)}; "
                "font-size: 16px; "
                "font-weight: 500;"
            )

            text_box.addWidget(date_label)
            text_box.addWidget(body)

            row.addLayout(text_box, 1)
            layout.addLayout(row)

        self.content_layout.addWidget(card)
