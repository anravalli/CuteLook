from __future__ import annotations

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLineEdit,
)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt, QPoint
from UnitTesting import RunTest
from enum import Enum


class FloatingImageButtonTypes(Enum):
    CLOSE = 0
    MINIMIZE = 1
    RAISE = 2
    LOWER = 3


def FloatingImageButtonFactory(
    button_type: FloatingImageButtonTypes, parent: QWidget = None
) -> FloatingControlButton:
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
                border-radius: 12px; /* make it circle shaped */
                font-weight: bold;
                border: 1px solid white;
            }}
            QPushButton:hover {{
                background-color: {hover_rgba};
            }}
        """)


if __name__ == "__main__":
    test_list = []

    p, f = RunTest(test_list)
    exit(f)
