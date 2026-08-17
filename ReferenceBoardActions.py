import typing

from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow,
    QAction,
    QToolBar,
    QMenu,
)
from PyQt5.QtGui import (
    QIcon,
)
from PyQt5.QtCore import QSize
from pydantic import BaseModel, ValidationError

class BoardActionConfigModel(BaseModel):
    custom_icon: list[str] = []
    theme_icon: list[str] = []
    text: str = ""
    tooltip: str = ""

class BoardActionBaseModel(BaseModel):
    action_name: str
    action_cfg: BoardActionConfigModel = None

class BoardActionsListModel(BaseModel):
    actions_list: list[BoardActionBaseModel] = []

class ReferenceBoardAction:
    icons: list[QIcon]
    action: QAction

    def __init__(self, action_cfg: BoardActionConfigModel, parent: QWidget, use_theme_icon: bool = False):
        icons = action_cfg.custom_icon
        self.icons = []
        if use_theme_icon:
            icons = action_cfg.theme_icon
        for icon in icons:
            self.icons.append(QIcon(icon))
        self.action = QAction(self.icons[0], action_cfg.text, parent)
        self.action.setStatusTip(action_cfg.tooltip)


class ReferenceBoardMenuFactory:

    _toolbar: QToolBar = None
    _context_menu: QMenu = None

    _use_os_theme: bool = False
    _board_actions: dict[str, ReferenceBoardAction] = None

    def __init__(self, parent: QMainWindow):

        self._board_actions = {}

        self._toolbar = parent.addToolBar("Main Toolbar")
        self._toolbar.setIconSize(QSize(24, 16))

        # create actions
        self.__load_action_config(parent)
        # add actions to toolbar
        for board_action in self._board_actions.values():
            if board_action is None:
                self._toolbar.addSeparator()
                continue
            self._toolbar.addAction(board_action.action)

        # add actions to context menu
        self._context_menu = QMenu(parent)
        for board_action in self._board_actions.values():
            if board_action is None:
                self._context_menu.addSeparator()
                continue
            self._context_menu.addAction(board_action.action)

    def __load_action_config(self, parent: QWidget):
        with open("./BoardActionsConfig.json", "r", encoding="utf-8") as f:
            json_actions = f.read()
        board_actions_model = BoardActionsListModel.model_validate_json(json_actions)
        separator_index = 0
        for action in board_actions_model.actions_list:
            # print(f"configuring {action.action_name} \n\t action: {action.action_cfg}")
            if action.action_name == "separator":
                sep = f"{action.action_name}{separator_index}"
                # print(f"adding separator: {sep}")
                self._board_actions[sep] = None
                separator_index =+ 1
            else:
                self._board_actions[action.action_name] = ReferenceBoardAction(action.action_cfg, parent)

    def connect(self, action_key: str, callback: typing.Callable[[], None]):
        try:
            action = self._board_actions[action_key].action
            action.triggered.connect(callback)
        except KeyError as e:
            print(e)

    def set_action_icon_index(self, action_name: str, index: int):
        action = self._board_actions[action_name].action
        icon_list = self._board_actions[action_name].icons
        if index < len(icon_list):
            action.setIcon(icon_list[index])
        else:
            print(f"WARNING: no icon for {action_name} at index {index}")

    def append_additional_actions(self, parent:QMainWindow, caption: str, callback: typing.Callable[[], None]):
        self._context_menu.addSeparator()
        action = QAction(caption, parent)
        action.triggered.connect(callback)
        self._context_menu.addAction(action)

    def __create_recent_boards_submenu(self, action: QAction) -> None :
        menu_apri = QMenu(self)

        # Personalizzazione estetica con QSS (stile stile "casella di testo")
        menu_apri.setStyleSheet("""
                    QMenu {
                        background-color: #ffffff;
                        border: 1px solid #b0b0b0;
                        border-radius: 4px;
                        padding: 4px;
                    }
                    QMenu::item {
                        padding: 6px 20px 6px 10px;
                        background-color: transparent;
                        color: #333333;
                    }
                    QMenu::item:selected {
                        background-color: #0078d4;
                        color: white;
                        border-radius: 2px;
                    }
                    QMenu::separator {
                        height: 1px;
                        background: #cccccc;
                        margin: 4px 0px 4px 0px;
                    }
                """)

        # Voci del menu
        # A. Voce principale per aprire il dialogo
        act_dialogo = menu_apri.addAction("Apri file...")
        act_dialogo.triggered.connect(self.openBoard)

        # B. Separatore
        menu_apri.addSeparator()

        # C. Lista dei file recenti (fino a 5)
        file_recenti = [
            "/percorso/del/documento1.txt",
            "/percorso/del/documento2.txt",
            "/percorso/del/progetto3.py",
            "/percorso/del/note4.md",
            "/percorso/del/dati5.csv",
        ]

        for i, file_path in enumerate(file_recenti, start=1):
            act_recente = menu_apri.addAction(f"Recente {i}: {file_path}")
            # Collega la scelta del file alla funzione di apertura
            act_recente.triggered.connect(
                lambda checked, path=file_path: self.apri_file_recente(path)
            )

        # 4. Assegna il menu all'azione e alla toolbar
        action.setMenu(menu_apri)
        #toolbar.addAction(action_apri)

        # Imposta il comportamento popup immediato
        button = self._toolbar.widgetForAction(action)
        if button:
            button.setPopupMode(button.ToolButtonPopupMode.InstantPopup)


    @property
    def toolbar(self) -> QToolBar:
        return self._toolbar

    @property
    def context_menu(self) -> QMenu:
        return self._context_menu
