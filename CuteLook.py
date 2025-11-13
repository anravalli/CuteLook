#!/usr/bin/env python3

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
from PyQt5.QtCore import Qt, QPoint

from ReferenceImageView import *
from ReferenceBoard import *
from UnitTesting import *


class MainWindow(QMainWindow):
    _opened_images = []
    _image_hidden = False
    _image_path = ""

    def __init__(self, image_path):
        super().__init__()

        self.setWindowTitle("Applicazione con Widget Floating")
        self.setGeometry(100, 100, 800, 600)
        self._image_path = image_path

        # Contenuto di sfondo
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_button_layout = QHBoxLayout()
        main_layout.addLayout(main_button_layout)

        open_button = QPushButton("open image")
        show_hide_button = QPushButton("show/hide")

        open_button.clicked.connect(self.openImage)
        show_hide_button.clicked.connect(self.showHideImages)

        main_button_layout.addWidget(open_button)
        main_button_layout.addWidget(show_hide_button)

        main_layout.addStretch(1)
        main_button_layout.addStretch(1)

    def openImage(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona File Immagine",
            "",  # Directory di default (vuoto = ultima usata o home)
            "Immagini (*.png *.jpg *.jpeg *.bmp *.gif)",  # Filtro dei file
        )
        self.addNewImage(file_path)

    def addNewImage(self, image_path):
        new_ref_image = ReferenceImageModel(image_path)
        # Creazione e Posizionamento del Widget Immagine Floating
        floating_image = FloatingImageWidget(image_path, parent=self)
        floating_image.move(self.width() - floating_image.width() - 20, 20)
        floating_image.show()
        self._opened_images.append(floating_image)

    def showHideImages(self):
        if self._image_hidden:
            for image in self._opened_images:
                image.show()
            self._image_hidden = False
        else:
            for image in self._opened_images:
                image.hide()
            self._image_hidden = True

    def setImageHide(self):
        self._image_hidden = True


# --- 3. Esecuzione dell'Applicazione ---
if __name__ == "__main__":
    app = QApplication(sys.argv)

    ref_board = ""
    if len(sys.argv) > 1:
        ref_board = sys.argv[1]
        print(f"Loading refernece board: {ref_board}")

    window = MainWindow(ref_board)
    window.show()
    sys.exit(app.exec_())
