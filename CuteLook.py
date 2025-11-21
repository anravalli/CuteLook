#!/usr/bin/env python3

import sys
from pathlib import Path

from ReferenceImageView import *
from ReferenceBoardView import *
from ReferenceBoard import *
from UnitTesting import *


class CuteLook:
    _boards: dict[int, ReferenceBoard] = {}

    def __init__(self, board_path: str = "") -> None:
        super().__init__()
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
            board_path = Path("")

        # 1.1 get the board id for this session
        next_id = len(self._boards)

        # 2. create the view
        board_view = ReferenceBoardView(next_id)

        # 3. create the controller
        new_board = ReferenceBoard(next_id, board_model, board_view)
        new_board.updateModifiedStatus(is_new)
        new_board.setBoardPath(board_path)

        # 4. connect relevant view's signals to manager (this)
        print(f"CuteLook - connect signals")
        board_view.close_board.connect(self.closeBoard)
        board_view.new_board.connect(self.openBoard)

        # 5. store the board
        self._boards[next_id] = new_board

    def closeBoard(self, board_id: int) -> None:
        print("CuteLook - closeBoard")
        try:
            if self._boards[board_id].close():
                print(f"removing board {board_id}")
                del self._boards[board_id]
                print(f"...removed")
            if not len(self._boards):
                print("Last board closed: exit")
                # the one below should not be needed
                # QApplication::instance().quit()

        except Exception as e:
            print(f'Excepltion cought while closing board "{board_id}":\n\t{e}')

    # callback for UI open_board action
    def openBoard(self, board_path: str) -> None:
        print(f"CuteLook - openBoard ({board_path})")
        self.boardFactory(board_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    ref_board = ""
    if len(sys.argv) > 1:
        ref_board = sys.argv[1]
        print(f"Loading refernece board: {ref_board}")
    cl = CuteLook(ref_board)
    sys.exit(app.exec_())
