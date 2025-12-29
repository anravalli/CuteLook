#!/usr/bin/env python3

import sys

from pathlib import Path
from platformdirs import user_config_dir

from ReferenceImageView import *
from ReferenceBoardView import *
from ReferenceBoard import *
from UnitTesting import *
from CuteLookConfig import *


class CuteLook:
    _boards: dict[int, ReferenceBoard] = {}
    _app_config: CuteLookConfig = CuteLookConfig()
    _app_config_path: Path = Path("~/.config/CuteLook.conf")

    def __init__(self, board_path: str = "") -> None:
        super().__init__()
        print("Loading Configuration")
        config_dir = Path(user_config_dir())
        self._app_config_path = config_dir / "CuteLook.conf"
        if self._app_config_path.exists() and self._app_config_path.is_file():
            self.loadConfig()
        else:
            config_dir.mkdir(parents=True, exist_ok=True)
            self.updateConfigFile()

        print(f"board_path: {board_path}")
        self.boardFactory(board_path)

    def boardFactory(self, path: str):
        print(f"CuteLook - boardFactory ({path})")
        # 1. create the model
        board_model = None
        board_path = Path(path)
        is_new = True

        if board_path.exists() and board_path.is_file():
            print(f"Opening board: {board_path}")
            with open(board_path, "r", encoding="utf-8") as f:
                json_board = f.read()
            board_model = ReferenceBoardModel.model_validate_json(json_board)
            is_new = False
        else:
            print("Creating new empty board")
            board_model = ReferenceBoardModel()
            board_path = Path(
                str(Path.home()) + "/" + board_model.board_name + ".refboard"
            )

        # 1.1 get the board id for this session
        next_id = len(self._boards)

        # 2. create the view
        board_view = ReferenceBoardView(next_id)

        # 3. create the controller
        new_board = ReferenceBoard(next_id, board_model, board_view)
        new_board.updateModifiedStatus(is_new)
        new_board._is_new = is_new
        new_board.setBoardPath(board_path)

        # 4. connect relevant view's signals to manager (this)
        print(f"CuteLook - connect signals")
        board_view.close_board.connect(self.closeBoard)
        board_view.new_board.connect(self.openBoard)

        # 5. store the board
        self._boards[next_id] = new_board

        if not new_board._is_new:
            self.addBoardToRecent(new_board)

    def closeBoard(self, board_id: int) -> None:
        print("CuteLook - closeBoard")
        try:
            if self._boards[board_id].canBeClosed():
                print(f"Storing state for board {board_id}")
                self.storeBoardState(board_id)
                self._boards[board_id].close()
                print(f"removing board {board_id}")
                del self._boards[board_id]
                print(f"...removed")

            if not len(self._boards):
                print("Last board closed: exit")

        except Exception as e:
            print(f'Excepltion cought while closing board "{board_id}":\n\t{e}')

    # callback for UI open_board action
    def openBoard(self, board_path: str) -> None:
        print(f"CuteLook - openBoard ({board_path})")
        self.boardFactory(board_path)
        self.updateConfigFile()

    def storeBoardState(self, board_id: int) -> None:
        board_view_state = self._boards[board_id].getViewState()
        board_path = self._boards[board_id]._board_path
        for saved_board in self._app_config.recent_boards:
            if board_path == saved_board.path:
                saved_board.view_state = board_view_state
                break
        self.updateConfigFile()

    def updateConfigFile(self) -> None:
        with open(self._app_config_path, "w", encoding="utf-8") as f:
            json_output = self._app_config.model_dump_json(indent=4)
            f.write(json_output)

    def loadConfig(self) -> None:
        with open(self._app_config_path, "r", encoding="utf-8") as f:
            json_cfg = f.read()
        self._app_config = CuteLookConfig.model_validate_json(json_cfg)

    def addBoardToRecent(self, board: ReferenceBoard) -> None:
        is_recent = False
        for i, saved_board in enumerate(self._app_config.recent_boards):
            if board._board_path == saved_board.path:
                board.restoreViewState(saved_board.view_state)
                self._app_config.recent_boards.pop(i)
                self._app_config.recent_boards.insert(0, saved_board)
                is_recent = True
                break
        if not is_recent:
            board_list_entry = RefBoard()
            board_list_entry.path = board._board_path
            board_list_entry.view_state = board.getViewState() #FIXME review needed
            self._app_config.recent_boards.append(board_list_entry)


if __name__ == "__main__":
    # QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    ref_board = ""
    if len(sys.argv) > 1:
        ref_board = sys.argv[1]
        print(f"Loading refernece board: {ref_board}")
    cl = CuteLook(ref_board)
    sys.exit(app.exec_())
