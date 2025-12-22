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
)
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QPoint, QSize, pyqtSignal

from ReferenceBoardModels import *


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


class FloatingImageWidget(QWidget):
    _pixmap: QPixmap = None
    _pixmap_size: QSize = None

    _image_model: ReferenceImageModel = None
    _image_name: str = ""

    _close_button: FloatingControlButton = None
    _hide_button: FloatingControlButton = None

    _covering_widget: QWidget = None
    _board = None

    image_modified: typing.ClassVar[pyqtSignal] = pyqtSignal()

    def __init__(
        self, image_name: str, image_model: ReferenceImageModel, board: QWidget = None
    ) -> None:
        super().__init__(board.getBoardArea())
        self._board = board

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self._drag_position = QPoint()

        self._pixmap = QPixmap(image_model.path)
        self._pixmap_size = self._pixmap.size()

        self.setFixedSize(self._pixmap_size)

        self._image_model = image_model
        self._image_name = image_name

        pos = self._image_model.view_position
        self.move(pos["x"], pos["y"])

        self.addControlButtons()

    def addControlButtons(self) -> None:
        self._close_button = FloatingControlButton("X", self)
        self._hide_button = FloatingControlButton("-", self)

        self._close_button.clicked.connect(self.close)
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
        self._board.setImageHide()
        super().hide()

    def close(self):
        self._board.closeImage(self._image_name)
        super().close()

    def _reposition_buttons(self):
        xc = self.width() - self._close_button.width() - 5
        xh = xc - self._hide_button.width() - 5
        y = 5
        self._close_button.move(xc, y)
        self._hide_button.move(xh, y)

    def enterEvent(self, event):
        self.show_buttons()
        i = 0
        children = self._board.getBoardArea().children()
        for child in children:
            print(f"child #{i}: {child}")
            if child == self:
                print("current image found at: #", i)
                break
            i += 1
        if i < len(children) - 1:
            print(f"self index {i} on {len(children) - 1}")
            self._covering_widget = children[i + 1]
            print(f"covering_widget is #{i}: {child}")
        else:
            self._covering_widget = None
        self.raise_()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hide_buttons()
        if self._covering_widget != None:
            print(f"restore staking ({self._covering_widget})")
            # self.stackUnder(self._covering_widget)
        else:
            print("keep current stacking")
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
            self.image_modified.emit()
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_position = QPoint()
        event.accept()

    def wheelEvent(self, event):
        zoom_factor = 1.1 if event.angleDelta().y() > 0 else 1 / 1.1
        new_size = self._pixmap_size * zoom_factor
        self.setFixedSize(new_size)
        self._reposition_buttons()
        self._pixmap_size = new_size
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        scaled_pixmap = self._pixmap.scaled(
            self._pixmap_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        painter.drawPixmap(0, 0, scaled_pixmap)
