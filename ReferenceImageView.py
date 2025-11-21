import sys
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
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QPoint, QSize

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

    def __init__(
        self, image_name: str, image_model: ReferenceImageModel, parent: QWidget = None
    ) -> None:
        super().__init__(parent)

        # new_ref_image.view_size["w"] = floating_image.width()
        # new_ref_image.view_size["h"] = floating_image.height()
        #
        # floating_image.move(self.width() - floating_image.width() - 20, 20)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self._drag_position = QPoint()

        self._pixmap = QPixmap(image_model.path)
        self._pixmap_size = self._pixmap.size()

        if self._pixmap.isNull():
            self.image_label = QLabel("Errore caricamento immagine", self)
            self.image_label.setAlignment(Qt.AlignCenter)
            self.image_label.setStyleSheet("background-color: lightgray; color: red;")
            self.setFixedSize(200, 100)
        else:
            self.image_label = QLabel(self)
            self.image_label.setPixmap(self._pixmap)
            self.image_label.setScaledContents(True)
            self.setFixedSize(self._pixmap_size)

            self.image_label.setGeometry(0, 0, self.width(), self.height())

        self._image_model = image_model
        self._image_name = image_name

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
        self.parent().setImageHide()
        super().hide()

    def close(self):
        self.parent().closeImage(self._image_name)
        super().close()

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
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_position = QPoint()
        event.accept()

    def wheelEvent(self, event):
        zoom_factor = 1.1 if event.angleDelta().y() > 0 else 1 / 1.1
        new_size = self._pixmap_size * zoom_factor
        scaled_pixmap = self._pixmap.scaled(
            new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)
        self.setFixedSize(new_size)
        # self.image_label.setGeometry(0, 0, new_size.width(), new_size.height())
        self._reposition_buttons()
        self._pixmap_size = new_size
        event.accept()
