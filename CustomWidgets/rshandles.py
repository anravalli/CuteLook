import typing
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QIcon, QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QPoint, QSize, pyqtSignal
from enum import Enum


class ResizeHandleType(Enum):
    TopLeft = 0
    TopMiddle = 1
    TopRight = 2
    RightMiddle = 3
    BottomRight = 4
    BottomMiddle = 5
    BottomLeft = 6
    LeftMiddle = 7


def ResizeHandleFactory():
    pass


class ResizeHandle(QWidget):
    _type: ResizeHandleType
    _size: int = 15
    _color: QColor = QColor("#00aaff")
    _hover_color_factor: int = 120

    _x_offset: int = 0
    _y_offset: int = 0
    _x_lock: bool = False
    _y_lock: bool = False
    _x_to_pos: bool = True
    _y_to_pos: bool = True

    view_port_resize: typing.ClassVar[pyqtSignal] = pyqtSignal(QPoint, QSize)

    def __init__(
        self,
        handle_type: ResizeHandleType = ResizeHandleType.TopLeft,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._hover_color = self._color.lighter(self._hover_color_factor)
        match handle_type:
            case ResizeHandleType.TopMiddle:
                self._x_offset = int(self._size / 2)
                self._y_offset = 0
                self._x_lock: bool = True
                self._y_lock: bool = False
                self._x_to_pos: bool = False
                self._y_to_pos: bool = True
            case ResizeHandleType.TopRight:
                self._x_offset = self._size
                self._y_offset = 0
                self._x_lock: bool = False
                self._y_lock: bool = False
                self._x_to_pos: bool = False
                self._y_to_pos: bool = True
            case ResizeHandleType.RightMiddle:
                self._x_offset = self._size
                self._y_offset = int(self._size / 2)
                self._x_lock: bool = False
                self._y_lock: bool = True
                self._x_to_pos: bool = False
                self._y_to_pos: bool = False
            case ResizeHandleType.BottomRight:
                self._x_offset = self._size
                self._y_offset = self._size
                self._x_lock: bool = False
                self._y_lock: bool = False
                self._x_to_pos: bool = False
                self._y_to_pos: bool = False
            case ResizeHandleType.BottomMiddle:
                self._x_offset = int(self._size / 2)
                self._y_offset = self._size
                self._x_lock: bool = True
                self._y_lock: bool = False
                self._x_to_pos: bool = False
                self._y_to_pos: bool = False
            case ResizeHandleType.BottomLeft:
                self._x_offset = 0
                self._y_offset = self._size
                self._x_lock: bool = False
                self._y_lock: bool = False
                self._x_to_pos: bool = True
                self._y_to_pos: bool = False
            case ResizeHandleType.LeftMiddle:
                self._x_offset = 0
                self._y_offset = int(self._size / 2)
                self._x_lock: bool = False
                self._y_lock: bool = True
                self._x_to_pos: bool = True
                self._y_to_pos: bool = False

        self._type = handle_type

    def setColor(self, color_str: str) -> None:
        self._color = QColor(color_str)

    def paintEvent(self, event):
        painter = QPainter(self)
        # pen = QPen(self._hover_color)
        brush = QBrush(self._color)
        # pen.setWidth(5)
        # painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(0, 0, self._size, self._size)
        event.accept()

    def move(self, ax: int, ay: int):
        x = ax - self._x_offset
        y = ay - self._y_offset
        super().move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_position = event.pos()
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # resize view port
            drag_amount = event.pos() - self._drag_position
            delta_pos = QPoint(0, 0)
            delta_size = QSize(0, 0)

            if not self._x_lock:
                if self._x_to_pos:
                    delta_pos.setX(drag_amount.x())
                else:
                    delta_size.setWidth(drag_amount.x())

            if not self._y_lock:
                if self._y_to_pos:
                    delta_pos.setY(drag_amount.y())
                else:
                    delta_size.setHeight(drag_amount.y())

            # self.move(pos)
            self.view_port_resize.emit(delta_pos, delta_size)

            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_position = QPoint()
        event.accept()


# if __name__ == "__main__":
#     test_list = []
#
#     p, f = RunTest(test_list)
#     exit(f)
