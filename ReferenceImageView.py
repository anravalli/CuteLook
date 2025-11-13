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


class FloatingImageWidget(QWidget):
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

        self.close_button.clicked.connect(self.hide)

        self._reposition_close_button()

        self.close_button.hide()

    def hide(self):
        self.parent().setImageHide()
        super().close()

    def _reposition_close_button(self):
        x = self.width() - self.close_button.width() - 5
        y = 5
        self.close_button.move(x, y)

    def enterEvent(self, event):
        self.close_button.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.close_button.hide()
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
        # self.setFixedSize(self._pixmap.size())
        self.image_label.setGeometry(0, 0, new_size.width(), new_size.height())
        self._reposition_close_button()
        self._pixmap_size = new_size
        event.accept()
