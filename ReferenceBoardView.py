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
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QPoint, pyqtSignal

from ReferenceImageView import *

# from ReferenceBoard import *
from ReferenceBoardModels import *
from UnitTesting import *


class ReferenceBoardView(QMainWindow):
    _opened_images: list = []
    _image_hidden: bool = False
    board_id: int = 0

    add_image: typing.ClassVar[pyqtSignal] = pyqtSignal(str, ReferenceImageModel)

    save_board: typing.ClassVar[pyqtSignal] = pyqtSignal(bool)
    # open_board: typing.ClassVar[pyqtSignal] = pyqtSignal()
    close_board: typing.ClassVar[pyqtSignal] = pyqtSignal(int)
    new_board: typing.ClassVar[pyqtSignal] = pyqtSignal(str)

    # def __init__(self, ctl: ReferenceBoard):
    def __init__(self, board_id: int):
        super().__init__()

        self._board_id = board_id

        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_button_layout = QHBoxLayout()
        main_layout.addLayout(main_button_layout)

        # reference board
        open_board_button = QPushButton("open")
        new_board_button = QPushButton("new")
        close_close_button = QPushButton("close")
        save_board_button = QPushButton("save")
        save_board_as_button = QPushButton("save as")

        new_board_button.clicked.connect(self.newBoard)
        open_board_button.clicked.connect(self.openBoard)
        save_board_button.clicked.connect(self.saveBoard)
        save_board_as_button.clicked.connect(self.saveBoardAs)
        close_close_button.clicked.connect(self.closeBoard)

        main_button_layout.addWidget(new_board_button)
        main_button_layout.addWidget(open_board_button)
        main_button_layout.addWidget(save_board_button)
        main_button_layout.addWidget(save_board_as_button)
        main_button_layout.addWidget(close_close_button)

        # reference images
        open_button = QPushButton("open image")
        show_hide_button = QPushButton("show/hide")

        open_button.clicked.connect(self.openImage)
        show_hide_button.clicked.connect(self.showHideImages)

        main_button_layout.addWidget(open_button)
        main_button_layout.addWidget(show_hide_button)

        main_layout.addStretch(1)
        main_button_layout.addStretch(1)

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

    def confirmClose(self) -> bool:
        reply = QMessageBox.question(
            self,
            "Close Confirm",
            "This board is modified. Close it anyway?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
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
            self.addNewImage(file_path)

    def addNewImage(self, image_path):
        path = pathlib.Path(image_path)
        floating_image = FloatingImageWidget(image_path, parent=self)

        new_ref_image = ReferenceImageModel()
        new_ref_image.path = path.absolute().as_posix()
        new_ref_image.view_size["w"] = floating_image.width()
        new_ref_image.view_size["h"] = floating_image.height()

        floating_image.move(self.width() - floating_image.width() - 20, 20)
        self.add_image.emit(path.stem, new_ref_image)
        self._opened_images.append(floating_image)

        floating_image.show()

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

    # TODO manage close event
    # def closeEvent(self, event: QCloseEvent):
    #     self.close_board.emit(path.stem, new_ref_image)
    #     event.ignore()


if __name__ == "__main__":
    test_list = []

    p, f = RunTest(test_list)
    exit(f)
