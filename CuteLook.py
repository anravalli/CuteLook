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
    QFileDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QPoint

# --- 1. Widget Riutilizzabile per l'Immagine e la Crocetta ---
class FloatingImageWidget(QWidget):
    """
    Un QWidget con un'immagine, trascinabile e con un bottone di chiusura
    visibile solo al passaggio del mouse.
    """
    _pixmap = None
    _pixmap_size = None
    def __init__(self, image_path, parent=None):
        super().__init__(parent)

        # --- Configurazione Base ---
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Variabili per il trascinamento
        self._drag_position = QPoint()

        # --- Contenuto: Immagine ---
        self._pixmap = QPixmap(image_path)
        self._pixmap_size = self._pixmap.size()

        if self._pixmap.isNull():
            # Caso di errore (gestione minimale)
            self.image_label = QLabel("Errore caricamento immagine", self)
            self.image_label.setAlignment(Qt.AlignCenter)
            self.image_label.setStyleSheet("background-color: lightgray; color: red;")
            self.setFixedSize(200, 100)
        else:
            # Etichetta Immagine
            self.image_label = QLabel(self)
            self.image_label.setPixmap(self._pixmap)
            self.image_label.setScaledContents(True)
            self.setFixedSize(self._pixmap_size)

            # Nota: La QLabel deve occupare l'intera area del FloatingImageWidget
            self.image_label.setGeometry(0, 0, self.width(), self.height())

        # --- Crocetta di Chiusura (Close Button) ---
        self.close_button = QPushButton("X", self)
        self.close_button.setFixedSize(25, 25)
        # Stile minimalista e rosso per la crocetta
        self.close_button.setStyleSheet("""
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

        # Collega il click del bottone al nascondere/chiudere il widget
        self.close_button.clicked.connect(self.hide)

        # Posiziona il bottone nell'angolo in alto a destra
        self._reposition_close_button()

        # All'inizio, nascondi la crocetta
        self.close_button.hide()

    def hide(self):
        self.parent().setImageHide()
        super().close()

    def _reposition_close_button(self):
        """Posiziona la crocetta nell'angolo in alto a destra con un piccolo margine."""
        x = self.width() - self.close_button.width() - 5
        y = 5
        self.close_button.move(x, y)

    # --- Eventi Hover per Mostrare/Nascondere la Crocetta ---
    def enterEvent(self, event):
        """Viene chiamato quando il mouse entra nell'area del widget."""
        self.close_button.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Viene chiamato quando il mouse esce dall'area del widget."""
        self.close_button.hide()
        super().leaveEvent(event)


    # --- Metodi per il Trascinamento ---
    # Questi metodi sono gli stessi dell'esempio precedente, garantiscono il trascinamento
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
        scaled_pixmap = self._pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.image_label.setPixmap(scaled_pixmap)
        #self.setFixedSize(self._pixmap.size())
        self.image_label.setGeometry(0, 0, new_size.width(), new_size.height())
        self._reposition_close_button()
        self._pixmap_size = new_size
        event.accept()


# --- 2. Finestra Principale dell'Applicazione ---
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
            "", # Directory di default (vuoto = ultima usata o home)
            "Immagini (*.png *.jpg *.jpeg *.bmp *.gif)" # Filtro dei file
        )
        self.addNewImage(file_path)

    def addNewImage(self, image_path):
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
if __name__ == '__main__':
    app = QApplication(sys.argv)

    if len(sys.argv) < 2:
        print("ERROR: missing file name")
        sys.exit(1)
    image_file = sys.argv[1]

    window = MainWindow(image_file)
    window.show()
    sys.exit(app.exec_())

