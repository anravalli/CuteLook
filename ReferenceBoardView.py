from __future__ import annotations
import typing
import pathlib
from PyQt5.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QAction,
    QToolBar,
    QMenu,
    QGraphicsView,
    QGraphicsScene,
)
from PyQt5.QtGui import (
    QCloseEvent,
    QIcon,
    QCursor,
    QGuiApplication,
    QTransform,
    QPainter,
)
from PyQt5.QtCore import Qt, QSize, QPoint, QRect, pyqtSignal

from ReferenceImageView import FloatingImageWidget
from CustomWidgets import FloatingLineEdit, SelectionBox, OverlayLabel

# from ReferenceBoard import *
from ReferenceBoardModels import ReferenceImageModel
from UnitTesting import RunTest


class ReferenceBoardAction:
    icon: QIcon = None
    action: QAction = None
    text: str = ""
    tooltip: str = ""


class ReferenceBoardView(QMainWindow):
    _opened_images: dict[str, FloatingImageWidget] = None
    _image_hidden: bool = False
    _use_os_theme: bool = False
    _board_actions: dict[str, ReferenceBoardAction] = None

    board_id: int = 0
    _board_area: BoardGraphicView = None
    _board_scene: QGraphicsScene = None
    _context_menu_pos: QPoint = None
    _toolbar: QToolBar = None

    _img_name_label: OverlayLabel = None
    _img_highlit_box: SelectionBox = None
    _current_highlighted_img = ""

    add_image: typing.ClassVar[pyqtSignal] = pyqtSignal(list)

    save_board: typing.ClassVar[pyqtSignal] = pyqtSignal(bool)
    close_board: typing.ClassVar[pyqtSignal] = pyqtSignal(int)
    new_board: typing.ClassVar[pyqtSignal] = pyqtSignal(str)
    rename_board: typing.ClassVar[pyqtSignal] = pyqtSignal(str)
    deselect_images: typing.ClassVar[pyqtSignal] = pyqtSignal()

    def __init__(self, board_id: int):
        super().__init__()

        self._board_actions = {}
        self._opened_images = {}
        self._board_id = board_id

        # self.setGeometry(100, 100, 800, 600)

        self._board_scene = QGraphicsScene()
        self._board_area = BoardGraphicView(self._board_scene)
        self._board_area.setStyleSheet("background-color: #232323;")

        self.setCentralWidget(self._board_area)

        self._toolbar = self.createToolbar()
        # connect actions signals do board callbacks
        self._board_actions["new_board"].action.triggered.connect(self.newBoard)
        self._board_actions["open_board"].action.triggered.connect(self.openBoard)
        self._board_actions["close_board"].action.triggered.connect(self.closeBoard)
        self._board_actions["save_board"].action.triggered.connect(self.saveBoard)
        self._board_actions["save_as_board"].action.triggered.connect(self.saveBoardAs)
        self._board_actions["add_image"].action.triggered.connect(self.openImage)
        self._board_actions["show_hide_image"].action.triggered.connect(
            self.showHideImages
        )

        self._board_area.setContextMenuPolicy(Qt.CustomContextMenu)
        self._board_area.customContextMenuRequested.connect(self.showBoardContexMenu)

        self._img_name_label = OverlayLabel(text="popoop asdkk", parent=self._board_area)
        self.updateImageNameLabelPosition()
        self._img_name_label.hide()
        self._img_highlit_box = SelectionBox(parent=self._board_area)
        self._img_highlit_box.hide()


    def updateImageNameLabelPosition(self):
        view_rect = self._board_area.rect()
        ol_pos_x = int((view_rect.width() -  self._img_name_label.width() ) / 2)
        ol_pos_y = int(view_rect.height() - 5 - self._img_name_label.height())
        self._img_name_label.move(ol_pos_x, ol_pos_y)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateImageNameLabelPosition()

    def showBoardContexMenu(self, point: QPoint) -> None:
        context_menu = QMenu(self)
        #     context_menu.setIcon("""
        #     QMenu::icon {
        #         width: 0px;
        #         margin-left: -5px;
        #     }
        # """)
        # print(f'--- board {self}"')
        # print(f'--- board dict: {self.__dict__}"')
        # print(f"--- board actions ref: {hex(id(self._board_actions))}")
        # print(f'--- board actions content: \n\t {self._board_actions}"')
        # print(f"--- _opened_images ref: {hex(id(self._opened_images))}")
        # print(f"--- _opened_images ref: \n\t{self._opened_images}")
        for board_action in self._board_actions.values():
            if board_action is None:
                context_menu.addSeparator()
                continue
            # print(f'--- action instance: {board_action.action}"')
            context_menu.addAction(board_action.action)
        self.addAdditionalActions(context_menu)
        self._context_menu_pos = self._board_area.mapToGlobal(point)
        context_menu.exec_(self._context_menu_pos)

    def addAdditionalActions(self, context_menu: QMenu):
        context_menu.addSeparator()
        rename = QAction("Rename Board", self)
        rename.triggered.connect(self.renameBoard)
        context_menu.addAction(rename)

    def renameBoard(self):
        le_pos = QPoint(self._context_menu_pos.x(), QCursor.pos().y())
        line_edit = FloatingLineEdit("New board name", pos=le_pos, parent=self)

        def accept_input():
            self.rename_board.emit(line_edit.text())
            line_edit.hide()

        line_edit.returnPressed.connect(accept_input)

    def createToolbar(self, themed=False) -> QToolBar:
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 16))
        # toolbar.setFloatable(True)
        # print(f"toolbar is floatable: {toolbar.isFloatable()}")
        # create actions
        self.configureBoardActions()
        # add actions to toolbar
        for board_action in self._board_actions.values():
            if board_action is None:
                toolbar.addSeparator()
                continue
            toolbar.addAction(board_action.action)

        return toolbar

    def configureBoardActions(self) -> None:
        self.initBoardActions()

        # add icons based on the current configuration
        if self._use_os_theme:
            # print("calling addBoardActionsIconsFromTheme")
            self.addBoardActionsIconsFromTheme()
        else:
            # print("calling initBoardActions")
            self.addBoardActionsIconsCustom()

        # create actions
        self.createBoardActions()

    def createBoardActions(self) -> None:
        # print("createBoardActions")
        for board_action in self._board_actions.values():
            if board_action is not None:
                # print(f'action "{board_action.text}"')
                board_action.action = QAction(
                    board_action.icon, board_action.text, self
                )
                board_action.action.setStatusTip(board_action.tooltip)
                # print(f'action instance: {board_action.action}"')

    def initBoardActions(self) -> None:
        # TODO read actions configuration from some configuration resource
        # print("initBoardActions")
        self._board_actions["new_board"] = ReferenceBoardAction()
        self._board_actions["new_board"].text = "New Board"
        self._board_actions["new_board"].tooltip = "Create a new board"

        self._board_actions["open_board"] = ReferenceBoardAction()
        self._board_actions["open_board"].text = "Open Board"
        self._board_actions["open_board"].tooltip = "Open an existing board"

        self._board_actions["save_board"] = ReferenceBoardAction()
        self._board_actions["save_board"].text = "Save Board"
        self._board_actions["save_board"].tooltip = "Save current board"

        self._board_actions["save_as_board"] = ReferenceBoardAction()
        self._board_actions["save_as_board"].text = "Save Board As"
        self._board_actions["save_as_board"].tooltip = "Save current board copy"

        self._board_actions["close_board"] = ReferenceBoardAction()
        self._board_actions["close_board"].text = "Close Board"
        self._board_actions["close_board"].tooltip = "Close current board"

        self._board_actions["separator"] = None

        self._board_actions["add_image"] = ReferenceBoardAction()
        self._board_actions["add_image"].text = "Add Image"
        self._board_actions["add_image"].tooltip = "Add a new reference image"

        self._board_actions["show_hide_image"] = ReferenceBoardAction()
        self._board_actions["show_hide_image"].text = "Show/Hide Images"
        self._board_actions["show_hide_image"].tooltip = "Show/Hide all images"

    def addBoardActionsIconsCustom(self) -> None:
        # print("addBoardActionsIconsCustom")
        self._board_actions["new_board"].icon = QIcon("icons/add-document.svg")
        self._board_actions["open_board"].icon = QIcon("icons/folder-open.svg")
        self._board_actions["close_board"].icon = QIcon("icons/cross.svg")
        self._board_actions["save_board"].icon = QIcon("icons/disk.svg")
        self._board_actions["save_as_board"].icon = QIcon("icons/floppy-disk-pen.svg")
        self._board_actions["add_image"].icon = QIcon("icons/add-image.svg")
        self._board_actions["show_hide_image"].icon = QIcon("icons/eye.svg")
        self._board_actions["show_hide_image"].icon2 = QIcon("icons/eye-crossed.svg")
        self._board_actions["show_hide_image"].icon3 = QIcon("icons/low-vision.svg")

    def addBoardActionsIconsFromTheme(self) -> None:
        self._board_actions["new_board"].icon = QIcon.fromTheme(
            "document-new", QIcon("icons/")
        )
        self._board_actions["open_board"].icon = QIcon.fromTheme(
            "document-new", QIcon("icons/")
        )
        self._board_actions["close_board"].icon = QIcon.fromTheme(
            "document-new", QIcon("icons/")
        )
        self._board_actions["save_board"].icon = QIcon.fromTheme(
            "document-save", QIcon("icons/save.png")
        )
        self._board_actions["save_as_board"].icon = QIcon.fromTheme(
            "document-new", QIcon("icons/")
        )

    def openBoard(self) -> None:
        board_ext = ".refboard"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a Reference Board",
            "",
            f"Reference Boards (*{board_ext})",
        )
        if file_path != "":
            self.new_board.emit(file_path)

    def newBoard(self) -> None:
        self.new_board.emit("")

    def closeBoard(self):
        self.close_board.emit(self._board_id)

    def closeEvent(self, event: QCloseEvent):
        # print(f"closeEvent - board window: {self._board_id}")
        self.close_board.emit(self._board_id)
        event.ignore()

    def confirmClose(self) -> bool:
        reply = QMessageBox.question(
            self,
            "Close Confirm",
            "This board is modified. Close it anyway?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        # print(f"reply: {reply}")
        # print(f"NO: {QMessageBox.No}")
        # print(f"Yes: {QMessageBox.Yes}")
        return reply == QMessageBox.Yes

    def saveBoard(self) -> None:
        self.save_board.emit(False)

    def saveBoardAs(self) -> None:
        self.save_board.emit(True)

    def openSaveDialog(self, default_path: str) -> str:
        # print(f"default_path name:  {default_path}")
        board_ext = ".refboard"
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Reference Board",
            default_path,
            f"Reference Boards (*{board_ext})",
        )
        if not file_name.endswith(board_ext) and file_name != "":
            file_name += board_ext
            # print(f"file name:  {file_name}")
        return file_name

    def openImage(self) -> None:
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select an Image",
            "",
            "Immagini (*.png *.jpg *.jpeg *.bmp *.gif)",
        )
        # build image model
        if len(file_paths) != 0:
            self.add_image.emit(file_paths)             

    def addStoredImage(
        self, image_name: str, image_model: ReferenceImageModel
    ) -> FloatingImageWidget:
        return self.inner_addImage(image_name, image_model)

    def addNewImage(
        self, image_name: str, image_model: ReferenceImageModel
    ) -> FloatingImageWidget:
        view_port_size = self._board_area.viewport().rect().size()
        return self.inner_addImage(image_name, image_model, view_port_size)

    def inner_addImage(
        self, image_name: str, image_model: ReferenceImageModel,
        view_port_size: QSize = None
    ) -> FloatingImageWidget:
        #we should inform the new image about the current scene geometry and scale?
        floating_image = FloatingImageWidget(image_name, image_model, view_port_size, parent=None)
        floating_image_proxy = self._board_scene.addWidget(floating_image)
        floating_image_proxy.setZValue(image_model.z_order)
        self._opened_images[image_name] = floating_image_proxy
        floating_image.show()
        return floating_image

    def closeImage(self, image_name: str) -> None:
        img = self._opened_images.pop(image_name)
        # Item is removed from scene by widget destructor
        # print(f'item in scene: {len(self._board_scene.items())}')
        img.deleteLater()

    def showMissingImageWarning(self, name: str, path: str) -> None:
        title = "Image file not found"
        message = (
            f'Can\'t open image "{name}".\n Please check if the path is valid:\n{path}'
        )
        QMessageBox.warning(self, title, message)

    def showHideImages(self) -> None:
        action = self._board_actions["show_hide_image"]
        if self._image_hidden:
            for image in self._opened_images.values():
                image.show()
            self._image_hidden = False
            action.action.setIcon(action.icon)
        else:
            for image in self._opened_images.values():
                image.hide()
            self._image_hidden = True
            action.action.setIcon(action.icon2)
            self._img_highlit_box.hide()
            self._img_name_label.hide()

    def setImageHide(self) -> None:
        self._image_hidden = True
        action = self._board_actions["show_hide_image"]
        action.action.setIcon(action.icon3)
        self._img_highlit_box.hide()
        self._img_name_label.hide()

    def mousePressEvent(self, event):
        self.deselect_images.emit()
        self._board_area.ignoreEvents(False)
        super().mousePressEvent(event)

    def deselectImages(self, images: list[str] = []) -> None:
        # print(f"images to deselect: {images}")
        if len(images):
            for image in images:
                self._opened_images[image].widget().deselect()

    def setImageZvalue(self, img_name: str, z_order: int) -> None:
        self._opened_images[img_name].setZValue(z_order)

    def updateImageHighlightBox(self, img_name: str) -> None:
        self._current_highlighted_img = img_name
        self.inner_updateImageHighlightBox()

    def inner_updateImageHighlightBox(self) -> None:
        img_name = self._current_highlighted_img
        img = self._opened_images[img_name].widget()
        new_pos = self._board_area.mapFromScene(img.pos())
        self._img_highlit_box.move(new_pos)
        self._img_highlit_box.setSize(img.size(), self._board_area.getScale())

    def viewportOffsetToScenePosition(self, offset: QPoint) -> QPoint:
        scene_pos = self._board_area.mapToScene(offset)
        return QPoint(int(scene_pos.x()), int(scene_pos.y()))

    def imgMouseOver(self, img_name: str, is_on: bool) -> None:
        if is_on:
            self._img_name_label.setText(img_name)
            self.updateImageHighlightBox(img_name)
            self._img_name_label.show()
            self._img_highlit_box.show()
        else:
            self._img_name_label.hide()
            self._img_highlit_box.hide()

class BoardGraphicView(QGraphicsView):
    _scale: float = 1
    _pan_start: QPoint
    _ignore_mouse_event: bool = False
    _space_pressed: bool = False
    _is_panning: bool = False

    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setRenderHint(QPainter.RenderHint.HighQualityAntialiasing)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # self.setCursor(Qt.ClosedHandCursor)

    def getScale(self) -> float:
        return self._scale

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._space_pressed = True
            event.accept()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._space_pressed = False
            event.accept()
        else:
            super().keyReleaseEvent(event)

    def _isPanStartEvent(self, event) -> bool:
        return event.button() == Qt.MiddleButton or (
            event.button() == Qt.LeftButton and self._space_pressed
        )

    def _isPanMoveEvent(self, event) -> bool:
        middle_button_drag = event.buttons() & Qt.MiddleButton
        space_left_button_drag = event.buttons() & Qt.LeftButton and self._space_pressed
        return middle_button_drag or space_left_button_drag

    def mousePressEvent(self, event):
        #print("mousePressEvent")
        self.unsetCursor()
        if self._isPanStartEvent(event):
            QGuiApplication.setOverrideCursor(Qt.CursorShape.ClosedHandCursor)
            self._pan_start_pos = event.pos()
            self._is_panning = True
            event.accept()
            print(f"mousePressEvent: initial scene rect: {self.sceneRect()}")
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_panning and self._isPanMoveEvent(event):
            drag = event.pos() - self._pan_start_pos
            self._panWithoutScrollbars(drag)
            self._pan_start_pos = event.pos()
            event.accept()
        else:
            # print("no mid")
            super().mouseMoveEvent(event)

    def _panWithoutScrollbars(self, drag: QPoint) -> None:
        drag_scene = self.mapToScene(self._pan_start_pos) - self.mapToScene(
            self._pan_start_pos + drag
        )
        visible_scene_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        moved_visible_rect = visible_scene_rect.translated(drag_scene)
        scene_rect = self.sceneRect()
        if not scene_rect.contains(moved_visible_rect):
            self.setSceneRect(
                scene_rect.united(moved_visible_rect).adjusted(-10, -10, 10, 10)
            )
        new_center = visible_scene_rect.center() + drag_scene
        self.centerOn(new_center)

    def mouseReleaseEvent(self, event):
        if self._is_panning and (
            event.button() == Qt.MiddleButton or event.button() == Qt.LeftButton
        ):
            QGuiApplication.restoreOverrideCursor()
            self._pan_start_pos = QPoint()
            self._is_panning = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        min_scale = 0.3
        max_scale = 5.0
        if (
            self._ignore_mouse_event
            or event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            super().wheelEvent(event)
        else:
            new_scale = self._scale
            #print(f"old scale: {new_scale}")
            scale_increment = 0.9
            if event.angleDelta().y() > 0:
                scale_increment = 1.1
            new_scale *= scale_increment
            if new_scale < min_scale:
                new_scale = min_scale
            elif new_scale > max_scale:
                new_scale = max_scale

            #print(f"new scale: {new_scale}")
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            transform = QTransform()
            transform.scale(new_scale, new_scale)
            self.setTransform(transform)

            self._scale = new_scale
            self.setTransformationAnchor(QGraphicsView.NoAnchor)
            self.parent().inner_updateImageHighlightBox()

    def ignoreEvents(self, ignore: bool = True) -> None:
        self._ignore_mouse_event = ignore

def _debug_Point(p: QPoint) -> str:
    return f"{p.x()},{p.y()}"


def _debug_Rect(r: QRect) -> str:
    return f"pos: {r.x()},{r.y()}; size: {r.width()}x{r.height()}"


if __name__ == "__main__":
    test_list = []

    p, f = RunTest(test_list)
    exit(f)
