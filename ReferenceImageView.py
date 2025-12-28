import sys
import typing
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QFileDialog,
    QSizePolicy
)
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QPoint, QSize, pyqtSignal

from ReferenceBoardModels import *
from enum import Enum, auto


class FloatingControlButton(QPushButton):
    def __init__(self, label: str = "X", parent: QWidget = None) -> None:
        super().__init__(label, parent)
        self.setFixedSize(25, 25)
        # Close Button style
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 0, 0, 150); /* Rosso semitrasparente */
                color: white;
                border-radius: 12px; /* Rende il bottone circolare */
                font-weight: bold;
                border: 1px solid white;
            }
            QPushButton:hover {
                background-color: red; /* Rosso solido all'hover */
            }
        """)

class FloatingImageState(Enum):
    NORMAL = 0
    HIDDEN = 1
    CLOSED = 2
    ZOOMED = 3
    PANNED = 4
    MOVED = 5

class FloatingImageWidget(QWidget):
    _pixmap: QPixmap = None
    _pixmap_size: QSize = None
    _drag_position: QPoint = QPoint()

    _image_model: ReferenceImageModel = None
    _image_name: str = ""

    _close_button: FloatingControlButton = None
    _hide_button: FloatingControlButton = None

    image_state_changed: typing.ClassVar[pyqtSignal] = pyqtSignal(str, FloatingImageState)

    def __init__(
        self, image_name: str, image_model: ReferenceImageModel, parent: QWidget = None
    ) -> None:
        super().__init__(parent)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self._image_model = image_model
        self._image_name = image_name

        self._pixmap = QPixmap(image_model.path)
        self._pixmap_size = self._pixmap.size()

        self.setFixedSize(self._pixmap_size * self._image_model.scale)
        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215) # QWIDGETSIZE_MAX
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


        pos = self._image_model.view_position
        self.move(pos["x"], pos["y"])

        self.addControlButtons()

    def addControlButtons(self) -> None:
        self._close_button = FloatingControlButton("X", self)
        self._hide_button = FloatingControlButton("-", self)

        self._close_button.clicked.connect(self.doClose)
        self._hide_button.clicked.connect(self.hide)

        self._reposition_buttons()

        self.hide_buttons()

    def hide_buttons(self):
        self._close_button.hide()
        self._hide_button.hide()

    def show_buttons(self):
        self._close_button.show()
        self._hide_button.show()

    def hide(self):
        self.image_state_changed.emit(self._image_name, FloatingImageState.HIDDEN)
        super().hide()

    def doClose(self):
        self.image_state_changed.emit(self._image_name, FloatingImageState.CLOSED)

    def _reposition_buttons(self):
        xc = self.width() - self._close_button.width() - 5
        xh = xc - self._hide_button.width() - 5
        y = 5
        self._close_button.move(xc, y)
        self._hide_button.move(xh, y)

    def enterEvent(self, event):
        self.show_buttons()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hide_buttons()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            pos = event.globalPos() - self._drag_position
            self.move(pos)
            self._image_model.view_position = {"x": pos.x(), "y": pos.y()}
            self.image_state_changed.emit(self._image_name, FloatingImageState.MOVED)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_position = QPoint()
        event.accept()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self._image_model.scale += 0.1
        else:
            self._image_model.scale += -0.1
        if self._image_model.scale < 0.1:
            self._image_model.scale = 0.1
        
        new_size = self._pixmap_size * self._image_model.scale
        self.setFixedSize(new_size)
        self._reposition_buttons()
        
        self.image_state_changed.emit(self._image_name, FloatingImageState.ZOOMED)
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        new_size = self._pixmap_size * self._image_model.scale
        scaled_pixmap = self._pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(0, 0, scaled_pixmap)
        event.accept()
