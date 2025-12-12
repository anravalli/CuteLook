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
    QMenu,
    QDialog,
    QLineEdit,
)
from PyQt5.QtGui import QPixmap, QCloseEvent, QIcon
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from UnitTesting import *


class FloatingInputDialog(QLineEdit):
    _text_input: str = None

    def __init__(
        self,
        title: str = "",
        label: str = "",
        pos: QPoint = QPoint(300, 300),
        width: int = 200,
        height: int = 100,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(pos, whidth, height)

        layout = QVBoxLayout(self)

        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText(label)

        self.line_edit.returnPressed.connect(self.accept_input)

        layout.addWidget(self.line_edit)
        self.setLayout(layout)

        self.line_edit.setFocus()

    def accept_input(self):
        self.text_input = self.line_edit.text()
        self.setPlaceholderText(label)
        self.accept()

    def get_text(self):
        return self.text_input


class FloatingLineEdit(QLineEdit):
    def __init__(
        self,
        label: str = "",
        pos: QPoint = QPoint(300, 300),
        width: int = 200,
        height: int = 30,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self.setGeometry(pos.x(), pos.y(), width, height)
        self.setPlaceholderText(label)
        self.setFocus()
        self.show()

    def accept_input(self):
        self.rename_board.emit(self.text())
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    test_list = []

    p, f = RunTest(test_list)
    exit(f)
