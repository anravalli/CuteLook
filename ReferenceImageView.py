import typing
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QPen, QColor
from PyQt5.QtCore import Qt, QPoint, QSize, pyqtSignal

from ReferenceBoardModels import ReferenceImageModel
from CustomWidgets import (
    FloatingControlButton,
    FloatingImageButtonTypes,
    FloatingImageButtonFactory,
    SelectionBox,
    ResizeHandle,
    ResizeHandleType,
)
from enum import Enum


class FloatingImageState(Enum):
    NORMAL = 0
    HIDDEN = 1
    CLOSED = 2
    ZOOMED = 3
    PANNED = 4
    MOVED = 5
    ZRAISED = 6
    ZLOWERED = 7
    SELECTED = 8
    UNSELECTED = 9


class FloatingImageWidget(QWidget):
    _pixmap: QPixmap = None
    _pixmap_size: QSize = None
    _pixmap_offset: QPoint = None
    _drag_position: QPoint = None
    _image_model: ReferenceImageModel = None
    _image_name: str = ""

    _close_button: FloatingControlButton = None
    _hide_button: FloatingControlButton = None

    _max_z: int = 99999
    _selected: bool = False

    image_state_changed: typing.ClassVar[pyqtSignal] = pyqtSignal(
        str, FloatingImageState
    )
    selected: typing.ClassVar[pyqtSignal] = pyqtSignal(str)

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
        self._pixmap_offset = QPoint(0, 0)

        self.setFixedSize(self._pixmap_size * self._image_model.scale)
        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)  # QWIDGETSIZE_MAX
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        pos = self._image_model.view_position
        self.move(pos["x"], pos["y"])

        self.addControlButtons()
        self.addHandles()

        # init _drag_position here to prevent random crash
        self._drag_position = QPoint()

    def addControlButtons(self) -> None:
        self._close_button = FloatingImageButtonFactory(
            FloatingImageButtonTypes.CLOSE, self
        )
        self._hide_button = FloatingImageButtonFactory(
            FloatingImageButtonTypes.MINIMIZE, self
        )

        self._rise_button = FloatingImageButtonFactory(
            FloatingImageButtonTypes.RAISE, self
        )
        self._lower_button = FloatingImageButtonFactory(
            FloatingImageButtonTypes.LOWER, self
        )

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
        self.image_state_changed.emit(self._image_name, FloatingImageState.ZRAISED)
        self.updateZetaOrder()  # assuming synchronous execution

    def doLower(self):
        self.image_state_changed.emit(self._image_name, FloatingImageState.ZLOWERED)
        self.updateZetaOrder()  # assuming synchronous execution

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
        super().leaveEvent(event)

    def updateZetaOrder(self) -> None:
        # print("updating z")
        proxy = self.graphicsProxyWidget()
        z = self._image_model.z_order
        if proxy:
            proxy.setZValue(z)

    def deselect(self):
        self._selected = False
        self.hide_buttons()
        self.hideHandles()
        self.updateZetaOrder()

    def mousePressEvent(self, event):
        modifiers = event.modifiers()
        if event.button() == Qt.LeftButton:
            if not self._selected:
                self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            else:
                self._drag_position = event.pos()
            if modifiers == Qt.KeyboardModifier.ControlModifier:
                # print("Click effettuato mentre CTRL era premuto")
                self.image_state_changed.emit(
                    self._image_name, FloatingImageState.SELECTED
                )
                proxy = self.graphicsProxyWidget()
                if proxy:
                    proxy.setZValue(self._max_z)
                self._selected = True
                self.showHandles()
            else:
                self.image_state_changed.emit(
                    self._image_name, FloatingImageState.UNSELECTED
                )
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if not self._selected:
                pos = event.globalPos() - self._drag_position
                # print(f"pos: {self.pos()}, new pos: {pos}")
                self.move(pos)
                self._image_model.view_position = {"x": pos.x(), "y": pos.y()}
            else:
                drag = event.pos() - self._drag_position
                self._drag_position = event.pos()
                print(f"drag: {drag}, _pixmap_offset: {self._pixmap_offset}")
                self._pixmap_offset = self._pixmap_offset - drag
                print(f"--- _pixmap_offset: {self._pixmap_offset}")
                self.update()

            self.image_state_changed.emit(self._image_name, FloatingImageState.MOVED)
            event.accept()

    def mouseReleaseEvent(self, event):
        # modifiers = event.modifiers()
        # self.image_state_changed.emit(self._image_name, FloatingImageState.SELECTED)
        self._drag_position = QPoint()
        # event.ignore()
        event.accept()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self._image_model.scale += 0.1
        else:
            self._image_model.scale += -0.1
        if self._image_model.scale < 0.1:
            self._image_model.scale = 0.1

        new_size = self._pixmap_size * self._image_model.scale
        # self.setFixedSize(new_size)
        self._reposition_buttons()
        self.repositionHandles()

        self.image_state_changed.emit(self._image_name, FloatingImageState.ZOOMED)
        self.update()
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        new_size = self._pixmap_size * self._image_model.scale
        scaled_pixmap = self._pixmap.scaled(
            new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        # print(f"pixmap offset: {-self._pixmap_offset.x()}, {-self._pixmap_offset.y()}")
        painter.drawPixmap(
            -self._pixmap_offset.x(), -self._pixmap_offset.y(), scaled_pixmap
        )

        event.accept()

    def addHandles(self):
        self._br_rhandle = ResizeHandle(ResizeHandleType.BottomRight, parent=self)
        self._br_rhandle.view_port_resize.connect(self.resizeViewPort)

        self._bl_rhandle = ResizeHandle(ResizeHandleType.BottomLeft, parent=self)
        self._bl_rhandle.view_port_resize.connect(self.resizeViewPort)

        self._tr_rhandle = ResizeHandle(ResizeHandleType.TopRight, parent=self)
        self._tr_rhandle.view_port_resize.connect(self.resizeViewPort)

        self._tl_rhandle = ResizeHandle(ResizeHandleType.TopLeft, parent=self)
        self._tl_rhandle.view_port_resize.connect(self.resizeViewPort)

        self._bm_rhandle = ResizeHandle(ResizeHandleType.BottomMiddle, parent=self)
        self._bm_rhandle.view_port_resize.connect(self.resizeViewPort)

        self._tm_rhandle = ResizeHandle(ResizeHandleType.TopMiddle, parent=self)
        self._tm_rhandle.view_port_resize.connect(self.resizeViewPort)

        self._rm_rhandle = ResizeHandle(ResizeHandleType.RightMiddle, parent=self)
        self._rm_rhandle.view_port_resize.connect(self.resizeViewPort)

        self._lm_rhandle = ResizeHandle(ResizeHandleType.LeftMiddle, parent=self)
        self._lm_rhandle.view_port_resize.connect(self.resizeViewPort)

        self.repositionHandles()
        self.hideHandles()

    def repositionHandles(self):
        self._br_rhandle.move(self.width(), self.height())
        self._bl_rhandle.move(0, self.height())
        self._tr_rhandle.move(self.width(), 0)
        self._tl_rhandle.move(0, 0)
        self._bm_rhandle.move(int(self.width() / 2), self.height())
        self._tm_rhandle.move(int(self.width() / 2), 0)
        self._rm_rhandle.move(self.width(), int(self.height() / 2))
        self._lm_rhandle.move(0, int(self.height() / 2))

    def showHandles(self):
        print("show resize handles")
        self._br_rhandle.show()
        self._bl_rhandle.show()
        self._tr_rhandle.show()
        self._tl_rhandle.show()
        self._bm_rhandle.show()
        self._tm_rhandle.show()
        self._rm_rhandle.show()
        self._lm_rhandle.show()

    def hideHandles(self):
        print("hide resize handles")
        self._br_rhandle.hide()
        self._bl_rhandle.hide()
        self._tr_rhandle.hide()
        self._tl_rhandle.hide()
        self._bm_rhandle.hide()
        self._tm_rhandle.hide()
        self._rm_rhandle.hide()
        self._lm_rhandle.hide()

    def resizeViewPort(self, delta_pos: QPoint, delta_size: QSize):
        print(f"delta_pos: {delta_pos}")
        self.move(self.pos() + delta_pos)
        self._pixmap_offset = self._pixmap_offset + delta_pos

        self.setFixedSize(
            self.size() + delta_size - QSize(delta_pos.x(), delta_pos.y())
        )

        self._reposition_buttons()
        self.repositionHandles()
