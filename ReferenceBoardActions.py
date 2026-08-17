import json
import typing
from enum import Enum

from PyQt5.QtWidgets import (
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
    custom_icon: list[QIcon]
    theme_icon: list[QIcon]
    action: QAction
    text: str = ""
    tooltip: str = ""

    def __init__(self):
        self.custom_icon = []
        self.theme_icon = []
        self.action = None
        self.text = ""
        self.tooltip = ""

    # def __init__(self, action: BoardActionBaseModel):
    #     self.custom_icon = action.custom_icon
    #     self.theme_icon = action.theme_icon


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
        self.load_action_config()
        self.__init_actions()
        self.__configure_board_actions()
        self.__create_actions(parent)
        # add actions to toolbar
        for board_action in self._board_actions.values():
            if board_action is None:
                self._toolbar.addSeparator()
                continue
            self._toolbar.addAction(board_action.action)

        self._context_menu = QMenu(parent)
        for board_action in self._board_actions.values():
            if board_action is None:
                self._context_menu.addSeparator()
                continue
            # print(f'--- action instance: {board_action.action}"')
            self._context_menu.addAction(board_action.action)

    def load_action_config(self):
        #json_actions = {}
        with open("./BoardActionsConfig.json", "r", encoding="utf-8") as f:
            json_actions = f.read()
        board_actions_model = BoardActionsListModel.model_validate_json(json_actions)
        print(f"dump the complete action list: \n\t{board_actions_model}")
        for action in board_actions_model.actions_list:
            print(f"dump {action.action_name} action: \n\t {action.action_cfg}")


    def connect(self, action_key: str, callback: typing.Callable[[], None]):
        try:
            action = self._board_actions[action_key].action
            action.triggered.connect(callback)
        except KeyError as e:
            print(e)

    def __configure_board_actions(self) -> None:
        # add icons based on the current configuration
        if self._use_os_theme:
            # print("calling addBoardActionsIconsFromTheme")
            self.__add_theme_icons_to_actions()
        else:
            # print("calling initBoardActions")
            self.__add_custom_icons_to_actions()


    def __init_actions(self) -> None:
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

        self._board_actions["separator2"] = None

        self._board_actions["fit_to_view"] = ReferenceBoardAction()
        self._board_actions["fit_to_view"].text = "Fit to screen"
        self._board_actions["fit_to_view"].tooltip = "Zoom in/out to make all images visibles"

        self._board_actions["reset_zoom"] = ReferenceBoardAction()
        self._board_actions["reset_zoom"].text = "Reset Zoom"
        self._board_actions["reset_zoom"].tooltip = "Reset the zoom level"

    def __add_custom_icons_to_actions(self) -> None:
        # print("addBoardActionsIconsCustom")
        self._board_actions["new_board"].custom_icon.append(QIcon("icons/add-document.svg"))
        # print(f"new_board num of icons: {len(self._board_actions["new_board"].custom_icon)}")
        self._board_actions["open_board"].custom_icon.append(QIcon("icons/folder-open.svg"))
        self._board_actions["close_board"].custom_icon.append(QIcon("icons/cross.svg"))
        self._board_actions["save_board"].custom_icon.append(QIcon("icons/disk.svg"))
        self._board_actions["save_as_board"].custom_icon.append(QIcon("icons/floppy-disk-pen.svg"))
        self._board_actions["add_image"].custom_icon.append(QIcon("icons/add-image.svg"))
        self._board_actions["show_hide_image"].custom_icon.append(QIcon("icons/eye.svg"))
        self._board_actions["show_hide_image"].custom_icon.append(QIcon("icons/eye-crossed.svg"))
        self._board_actions["show_hide_image"].custom_icon.append(QIcon("icons/low-vision.svg"))
        self._board_actions["fit_to_view"].custom_icon.append(QIcon("icons/dark_zoom-fit.svg"))
        self._board_actions["reset_zoom"].custom_icon.append(QIcon("icons/dark_zoom-100.svg"))
        # print(f"new_board num of icons: {len(self._board_actions["new_board"].custom_icon)}")
        #print(f"actions: {json.dumps(self._board_actions)}")

    def __add_theme_icons_to_actions(self) -> None:
        self._board_actions["new_board"].theme_icon.append(QIcon.fromTheme(
            "document-new", QIcon("icons/"))
        )
        self._board_actions["open_board"].theme_icon.append(QIcon.fromTheme(
            "document-new", QIcon("icons/"))
        )
        self._board_actions["close_board"].theme_icon.append(QIcon.fromTheme(
            "document-new", QIcon("icons/"))
        )
        self._board_actions["save_board"].theme_icon.append(QIcon.fromTheme(
            "document-save", QIcon("icons/save.png"))
        )
        self._board_actions["save_as_board"].theme_icon.append(QIcon.fromTheme(
            "document-new", QIcon("icons/"))
        )

    def __create_actions(self, parent: QMainWindow) -> None:
        # print("createBoardActions")
        for board_action in self._board_actions.values():
            if board_action is not None:
                print(f'action "{board_action.text}"')
                board_action.action = QAction(
                    board_action.custom_icon[0], board_action.text, parent
                )
                board_action.action.setStatusTip(board_action.tooltip)
                # print(f'action instance: {board_action.action}"')

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
