from PyQt5.QtWidgets import QSizePolicy, QWidget
from PyQt5.QtGui import QColor, QFontMetrics, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QRectF, QSize


class OverlayLabel(QWidget):
    def __init__(
        self,
        text: str = "",
        parent: QWidget = None,
        padding: QSize = QSize(10, 6),
        radius: int = 8,
        background_color: QColor = QColor(0, 0, 0, 160),
        text_color: QColor = QColor("#FFFFFF"),
        border_color: QColor = QColor(255, 255, 255, 180),
    ) -> None:
        super().__init__(parent)
        self._text = text
        self._padding = padding
        self._radius = radius
        self._background_color = background_color
        self._text_color = text_color
        self._border_color = border_color

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._update_size()

    def setText(self, new_text: str) -> None:
        self._text = new_text
        self._update_size()
        self.update()

    def text(self) -> str:
        return self._text

    def setPos(self, x: int, y: int) -> None:
        self.move(QPoint(x, y))

    def setPadding(self, horizontal: int, vertical: int) -> None:
        self._padding = QSize(horizontal, vertical)
        self._update_size()
        self.update()

    def sizeHint(self) -> QSize:
        metrics = QFontMetrics(self.font())
        text_size = metrics.size(Qt.TextSingleLine, self._text)
        return QSize(
            text_size.width() + self._padding.width() * 2,
            text_size.height() + self._padding.height() * 2,
        )

    def _update_size(self) -> None:
        self.setFixedSize(self.sizeHint())
        self.updateGeometry()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        painter.setBrush(self._background_color)
        painter.setPen(QPen(self._border_color, 1))
        painter.drawRoundedRect(rect, self._radius, self._radius)

        text_rect = self.rect().adjusted(
            self._padding.width(),
            self._padding.height(),
            -self._padding.width(),
            -self._padding.height(),
        )
        painter.setPen(self._text_color)
        painter.drawText(text_rect, Qt.AlignCenter | Qt.TextSingleLine, self._text)
        event.accept()
