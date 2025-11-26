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
    QMessageBox,
    QAction,
    QToolBar,
    QStyle,
)
from PyQt5.QtGui import QPixmap, QCloseEvent, QIcon
from PyQt5.QtCore import Qt, QPoint, pyqtSignal

from ReferenceImageView import *

# from ReferenceBoard import *
from ReferenceBoardModels import *
from UnitTesting import *


class ReferenceBoardAction:
    icon: QIcon = None
    action: QAction = None
    text: str = ""
    tooltip: str = ""


class ReferenceBoardView(QMainWindow):
    _opened_images: dict[str, ReferenceImageModel] = {}
    _image_hidden: bool = False
    _use_os_theme: bool = False
    _board_actions: dict[str, ReferenceBoardAction] = {}

    board_id: int = 0

    add_image: typing.ClassVar[pyqtSignal] = pyqtSignal(pathlib.Path)
    close_image: typing.ClassVar[pyqtSignal] = pyqtSignal(str)

    save_board: typing.ClassVar[pyqtSignal] = pyqtSignal(bool)
    close_board: typing.ClassVar[pyqtSignal] = pyqtSignal(int)
    new_board: typing.ClassVar[pyqtSignal] = pyqtSignal(str)

    def __init__(self, board_id: int):
        super().__init__()

        self._board_id = board_id

        self.setGeometry(100, 100, 800, 600)

        board_area = QWidget()
        board_area.setStyleSheet("background-color: #232323;")

        self.setCentralWidget(board_area)

        toolbar = self.createToolbar()
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

    def createToolbar(self, themed=False) -> QToolBar:
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 16))
        # create actions
        self.configureBoardActions()
        # add actions to toolbar
        for board_action in self._board_actions.values():
            if board_action == None:
                toolbar.addSeparator()
                continue
            toolbar.addAction(board_action.action)

        return toolbar

    def configureBoardActions(self) -> None:
        self.initBoardActions()

        # add icons based on the current configuration
        if self._use_os_theme:
            print("calling addBoardActionsIconsFromTheme")
            self.addBoardActionsIconsFromTheme()
        else:
            print("calling initBoardActions")
            self.addBoardActionsIconsCustom()

        # create actions
        self.createBoardActions()

    def createBoardActions(self) -> None:
        for board_action in self._board_actions.values():
            if not board_action == None:
                print(f'action "{board_action.text}"')
                board_action.action = QAction(
                    board_action.icon, board_action.text, self
                )
                board_action.action.setStatusTip(board_action.tooltip)

    def initBoardActions(self) -> None:
        # TODO read actions configuration from some configuration resource
        print("initBoardActions")
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
        print("addBoardActionsIconsCustom")
        self._board_actions["new_board"].icon = QIcon("icons/add-document.svg")
        self._board_actions["open_board"].icon = QIcon("icons/folder-open.svg")
        self._board_actions["close_board"].icon = QIcon("icons/cross.svg")
        self._board_actions["save_board"].icon = QIcon("icons/disk.svg")
        self._board_actions["save_as_board"].icon = QIcon("icons/floppy-disk-pen.svg")
        print(f'add_image icon "{self._board_actions["add_image"].icon}"')
        self._board_actions["add_image"].icon = QIcon("icons/add-image.svg")
        print(f'add_image icon "{self._board_actions["add_image"].icon}"')
        self._board_actions["show_hide_image"].icon = QIcon("icons/eye.svg")
        self._board_actions["show_hide_image"].icon2 = QIcon("icons/eye-crossed.svg")

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
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a Reference Board",
            "",
            "Reference Boards (*.refboard)",
        )
        if file_path != "":
            self.new_board.emit(file_path)

    def newBoard(self) -> None:
        self.new_board.emit("")

    def closeBoard(self):
        self.close_board.emit(self._board_id)

    def closeEvent(self, event: QCloseEvent):
        print(f"closeEvent - board window: {self._board_id}")
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
        print(f"reply: {reply}")
        print(f"NO: {QMessageBox.No}")
        print(f"Yes: {QMessageBox.Yes}")
        return reply == QMessageBox.Yes

    def saveBoard(self) -> None:
        self.save_board.emit(False)

    def saveBoardAs(self) -> None:
        self.save_board.emit(True)

    def openSaveDialog(self) -> str:
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Reference Board",
            "",
            "Reference Boards (*.refboard)",
        )
        return file_name

    def openImage(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select an Image",
            "",
            "Immagini (*.png *.jpg *.jpeg *.bmp *.gif)",
        )
        # build image model
        if file_path != "":
            path = pathlib.Path(file_path)
            self.add_image.emit(path)

    def addImage(self, image_name: str, image_model: ReferenceImageModel):
        floating_image = FloatingImageWidget(image_name, image_model, parent=self)

        self._opened_images[image_name] = floating_image

        floating_image.show()

    def closeImage(self, image_name: str):
        img = self._opened_images.pop(image_name)
        img.deleteLater()
        self.close_image.emit(image_name)

    def showMissingImageWarning(self, name: str, path: str) -> None:
        title = "Image file not found"
        message = (
            f'Can\'t open image "{name}".\n Please check if the path is valid:\n{path}'
        )
        dialog = QMessageBox.warning(self, title, message)

    def showHideImages(self):
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

    def setImageHide(self):
        self._image_hidden = True


if __name__ == "__main__":
    test_list = []

    p, f = RunTest(test_list)
    exit(f)
