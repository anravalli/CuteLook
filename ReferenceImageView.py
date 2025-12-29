import sys
import typing
from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy
)
from PyQt5.QtGui import QPixmap, QPainter, QIcon
from PyQt5.QtCore import Qt, QPoint, QSize, pyqtSignal

from ReferenceBoardModels import *
from CustomWidget import FloatingControlButton
from enum import Enum, auto


class FloatingImageButtonTypes(Enum):
    CLOSE = 0
    MINIMIZE = 1
    RAISE = 2
    LOWER = 3

class FloatingImageState(Enum):
    NORMAL = 0
    HIDDEN = 1
    CLOSED = 2
    ZOOMED = 3
    PANNED = 4
    MOVED = 5
    ZCHANGED = 6
    
def FloatingImageButtonFactory(button_type: FloatingImageButtonTypes, parent: QWidget = None) -> FloatingControlButton:
    icon = None
    color = ""
    match button_type:
        case FloatingImageButtonTypes.CLOSE:
            icon = QIcon("icons/cross-small.svg")
            color = "red"
        case FloatingImageButtonTypes.MINIMIZE:
            icon = QIcon("icons/minus-small.svg")
            color = "yellow"
        case FloatingImageButtonTypes.RAISE:
            icon = QIcon("icons/arrow-up.svg")
            color = "#1f00f0"
        case FloatingImageButtonTypes.LOWER:
            icon = QIcon("icons/arrow-down.svg")
            color = "#1f00f0"
    
    button = FloatingControlButton(icon, color, parent)
    return button

class FloatingImageWidget(QWidget):
    _pixmap: QPixmap = None
    _pixmap_size: QSize = None
    _drag_position: QPoint = QPoint()

    _image_model: ReferenceImageModel = None
    _image_name: str = ""

    _close_button: FloatingControlButton = None
    _hide_button: FloatingControlButton = None
    
    _max_z: int = 99999
    _selected: bool = False 

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
        self._close_button = FloatingImageButtonFactory(FloatingImageButtonTypes.CLOSE, self)
        self._hide_button = FloatingImageButtonFactory(FloatingImageButtonTypes.MINIMIZE, self)
        
        self._rise_button = FloatingImageButtonFactory(FloatingImageButtonTypes.RAISE, self)
        self._lower_button = FloatingImageButtonFactory(FloatingImageButtonTypes.LOWER, self)

        self._close_button.clicked.connect(self.doClose)
        self._hide_button.clicked.connect(self.hide)
        self._rise_button.clicked.connect(self.doRaise)
        self._lower_button.clicked.connect(self.doLower)
        
        self._reposition_buttons()

        self.hide_buttons()

    def hide_buttons(self):
        self._close_button.hide()
        self._hide_button.hide()
        self._rise_button.hide()
        self._lower_button.hide()
        
    def show_buttons(self):
        self._close_button.show()
        self._hide_button.show()
        self._rise_button.show()
        self._lower_button.show()
        
    def hide(self):
        self.image_state_changed.emit(self._image_name, FloatingImageState.HIDDEN)
        super().hide()

    def doClose(self):
        self.image_state_changed.emit(self._image_name, FloatingImageState.CLOSED)
    
    def doRaise(self):
        self._image_model.z_order += 1
        self.updateZetaOrder()
        self.image_state_changed.emit(self._image_name, FloatingImageState.ZCHANGED)
    
    def doLower(self):
        self._image_model.z_order += -1
        self.updateZetaOrder()
        self.image_state_changed.emit(self._image_name, FloatingImageState.ZCHANGED)
    
    def _reposition_buttons(self):
        xc = self.width() - self._close_button.width() - 5
        xh = xc - self._hide_button.width() - 5
        xr = 0
        xl = xr + self._rise_button.width()
        y = 5
        self._close_button.move(xc, y)
        self._hide_button.move(xh, y)
        self._rise_button.move(xr, y)
        self._lower_button.move(xl, y)
        
    def enterEvent(self, event):
        self.show_buttons()
        
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self._selected:
            self.hide_buttons()
        #self.updateZetaOrder()
        super().leaveEvent(event)
        
    def updateZetaOrder(self) -> None:
        proxy = self.graphicsProxyWidget()
        z = self._image_model.z_order
        if proxy:
            proxy.setZValue(z)
            
    def deselect(self):
        self._selected = False
        self.hide_buttons()
        self.updateZetaOrder()

    def mousePressEvent(self, event):
        modifiers = event.modifiers()
        if event.button() == Qt.LeftButton:
            if modifiers == Qt.KeyboardModifier.ControlModifier:
                print("Click effettuato mentre CTRL era premuto")
                proxy = self.graphicsProxyWidget()
                if proxy:
                    proxy.setZValue(self._max_z)
                self._selected = True
                
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
        
#     def keyPressEvent(self, event):
#         # Esempio 1: Flag attivo finché il tasto è premuto
#         if event.key() == Qt.Key.Key_Shift:
#             self.is_selection_mode = True
#             print("Modalità selezione ATTIVA")
#         
#         # Esempio 2: Flag "Toggle" (premo S per cambiare stato)
#         if event.key() == Qt.Key.Key_S:
#             self.is_selection_mode = not self.is_selection_mode
#             print(f"Stato flag S: {self.is_selection_mode}")
# 
#         # IMPORTANTE: Passa l'evento alla classe base se vuoi 
#         # che le altre funzioni di Qt continuino a lavorare
#         super().keyPressEvent(event)
# 
#     def keyReleaseEvent(self, event):
#         # Ripristiniamo il flag quando il tasto viene rilasciato
#         if event.key() == Qt.Key.Key_Shift:
#             self.is_selection_mode = False
#             print("Modalità selezione DISATTIVATA")
#         
#         super().keyReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        new_size = self._pixmap_size * self._image_model.scale
        scaled_pixmap = self._pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(0, 0, scaled_pixmap)
        event.accept()
