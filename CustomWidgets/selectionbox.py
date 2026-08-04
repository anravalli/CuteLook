from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QSize

class SelectionBox(QWidget):
    _size: QSize = None,
    def __init__(
        self,   
        line_width: int = 2,
        color_str: str = "#FF5733",
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._lwidth = line_width
        self._color = QColor(color_str)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def setSize(self, new_size: QSize, scale):
        self._size = (new_size+QSize(1,1))*scale
        self.setFixedSize(self._size)
        self.updateGeometry()
        self.update()

    def move(self, pos: QPoint):
        new_pos = pos + QPoint(-1,-1)
        super().move(new_pos)

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(self._color)
        pen.setWidth(self._lwidth)
        painter.setPen(pen)
        #painter.setBrush(QColor("#FFFFFF"))
        painter.drawRect(0, 0, self._size.width(), self._size.height())
        event.accept()
