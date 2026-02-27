from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt, QPoint
from UnitTesting import RunTest


def ResizeHandleFactory():
    pass


class ResizeHandle(QWidget):
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
