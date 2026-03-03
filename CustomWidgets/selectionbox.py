from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QPoint, QSize


class SelectionBox(QWidget):
    def __init__(
        self,
        size: QSize = None,
        line_width: int = 2,
        color_str: str = "#FF5733",
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self.lwidth = line_width
        self.size = size
        self.color = QColor(color_str)

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(self.color)
        pen.setWidth(self.lwidth)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.size.width(), self.size.height())
        event.accept()
