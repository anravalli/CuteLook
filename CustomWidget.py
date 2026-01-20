# import typing
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLineEdit,
)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt, QPoint
from UnitTesting import RunTest


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
        self.setGeometry(pos, width, height)

        layout = QVBoxLayout(self)

        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText(label)

        self.line_edit.returnPressed.connect(self.accept_input)

        layout.addWidget(self.line_edit)
        self.setLayout(layout)

        self.line_edit.setFocus()

    def accept_input(self):
        self.text_input = self.line_edit.text()
        self.setPlaceholderText(self.label)
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
        self.setGeometry(pos.x(), round(pos.y() - height / 2), width, height)
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

    def focusOutEvent(self, event):
        self.close()
        super().focusOutEvent(event)


class FloatingControlButton(QPushButton):
    def __init__(
        self, icon: QIcon = None, color_str: str = "#ff0000", parent: QWidget = None
    ) -> None:
        super().__init__(parent)
        self.setFixedSize(25, 25)
        self.setIcon(icon)

        # Button style
        alpha = 120
        color = QColor(color_str)
        base_rgba = f"rgba({color.red()}, {color.green()}, {color.blue()}, {alpha})"
        hover_color = color.lighter(120)
        hover_rgba = (
            f"rgb({hover_color.red()}, {hover_color.green()}, {hover_color.blue()})"
        )

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {base_rgba};
                color: white;
                border-radius: 12px; /* Rende il bottone circolare */
                font-weight: bold;
                border: 1px solid white;
            }}
            QPushButton:hover {{
                background-color: {hover_rgba},
            }}
        """)


if __name__ == "__main__":
    test_list = []

    p, f = RunTest(test_list)
    exit(f)
