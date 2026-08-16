import typing

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QSize, QRect


class SelectionBox(QWidget):
    _size: QSize = None,
    _line_width: int = 2
    _inset: int = 1

    def __init__(
        self,   
        line_width: int = 1,
        color_str: str = "#FF5733",
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        #self._line_width = line_width
        self._color = QColor(color_str)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    # @typing.overload
    def setSize(self, new_size: QSize, scale):
        #print(f"new size: {new_size}, scale: {scale}")
        size_adjust = QSize(self._line_width, self._line_width)
        self._size = new_size*scale+size_adjust
        #print(f"size adjusted: {self._size}")
        self.setFixedSize(self._size)
        self.updateGeometry()
        self.update()

    # @typing.overload
    # def setSize(self, rect: QRect, scale: float | int) -> None:
    #     print(f"rect: {rect}, scale: {scale}")
    #     scaled_rect = rect.scale(self._scale)
    #     self._size = new_size*scale+size_adjust
    #     print(f"size adjusted: {self._size}")
    #     self.setFixedSize(self._size)
    #     self.updateGeometry()
    #     self.update()

    def move(self, pos: QPoint):
        new_pos = pos + QPoint(int(-self._line_width/2),int(-self._line_width/2))
        super().move(new_pos)

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(self._color)
        pen.setWidth(self._line_width)
        painter.setPen(pen)
        #painter.setBrush(QColor("#FFFFFF"))
        painter.drawRect(self._inset, self._inset, self._size.width()-self._inset, self._size.height()-self._inset)
        event.accept()
