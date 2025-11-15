import json
import pathlib

from UnitTesting import *

from ReferenceBoardModels import *
from ReferenceBoardView import *


# Reference Board controller
class ReferenceBoard:
    _reference_board: ReferenceBoardModel = None
    _board_window: ReferenceBoardView = None

    _board_path: pathlib.Path = "./unknown.refboard"
    _modified: bool = False

    def __init__(
        self, board_id: int, model: ReferenceBoardModel, view: ReferenceBoardView
    ) -> None:
        self._board_id = board_id
        self._reference_board = model
        self._board_window = view
        self._board_window.setWindowTitle(model.board_name)

        self._board_window.add_image.connect(self.addImage)
        self._board_window.save_board.connect(self.save)
        # self._board_window.close_board.connect(self.close)
        self._board_window.show()

    def view(self) -> ReferenceBoardView:
        return self._board_window

    def setBoardPath(self, path: pathlib.Path) -> None:
        self._board_path = path

    def updateModifiedStatus(self, modified: bool) -> None:
        title = self._reference_board.board_name
        if modified:
            title = f"*{title}"
        self._modified = modified
        self._board_window.setWindowTitle(title)

    def save(self, change_name: bool = False) -> None:
        print(f"saving board: {self._reference_board.board_name}")
        print(f"...to: {self._board_path}")

        save_to = self._board_path
        if save_to == pathlib.Path("") or change_name:
            save_to = self._board_window.openSaveDialog()
            if save_to == pathlib.Path(""):
                # abort
                return
            else:
                self._board_path = save_to
                self._modified = True

        # throw if error/fails
        if self._modified:
            # Exceptions will be farwarded to the caller
            print(f"...to: {self._board_path}")
            with open(save_to, "w", encoding="utf-8") as f:
                json_output = self._reference_board.model_dump_json(indent=4)
                f.write(json_output)
            self.updateModifiedStatus(False)

    # need unit test
    # def saveAs(self, new_path: pathlib.Path) -> None:
    #     # throw if error/fails
    #     self._board_path = new_path
    #     self.updateModifiedStatus(False)
    #     self.save()

    # need unit test
    def close(self) -> None:
        print("ReferenceBoard - closeBoard")
        if self._modified:
            self._modified = not self._board_window.confirmClose()

        if not self._modified:
            self._board_window.close()  # may be a loop here

    # need unit test
    def addImage(self, name: str, new_image: ReferenceImageModel) -> None:
        print(f'adding image "{name}"')
        i = 1
        while name in self._reference_board.reference_images.keys():
            name = f"{name}-{i}"
            i += 1
        self._reference_board.reference_images[name] = new_image
        self.updateModifiedStatus(True)
        print(f'added image "{name}"')

    # need unit test
    def deleteImage(self, name: str) -> None:
        # exception shall be handled by caller
        del self._reference_board.reference_images[name]

    # need unit test
    def rename(new_name: str) -> None:
        self._reference_board.board_name = new_name
        self._board_window.setWindowTitle(new_name)
        self.updateModifiedStatus(True)

    def name(self) -> str:
        return self._reference_board.board_name

    # need unit test
    def renameImage(self, old_name: str, new_name: str) -> None:
        # check if the new name is the same as the old one
        # assert old_name != new_name, f'New name is equal to current one'

        # check if the new name is already in use
        assert new_name not in self._reference_board.reference_images.keys(), (
            f"Name already in use"
        )

        # do rename (exception shall be handled by caller)
        refImage = self._reference_board.reference_images.pop(old_name, None)
        self._reference_board.reference_images[new_name] = refImage
        self.updateModifiedStatus(True)

    # need unit test
    def getImageModel(self, img_name: str) -> ReferenceImageModel:
        assert img_name in self._reference_board.reference_images.keys(), (
            f'Image "{img_name}" not part of this board'
        )
        return self._reference_board.reference_images[img_name]

    def getModel(self) -> ReferenceBoardModel:
        return self._reference_board


import os

test_data = {
    "board_file_name": "./pippo.refboard",
    "json_refboard": '{"board_name": "test",\n\
        "reference_images": \n{ "pippo": \n{"path": "./pippo.png", "zoom": "2"}, "pluto": \n{"path": "./pluto.png", "zoom": "1", "image_center": {"x": 256.0, "y": 256.0}, "view_size": {"w": 512.0, "h": 512.0}}\n }\n }\n',
}


class FakeReferenceBoardView:
    def show(self):
        print("FakeReferenceBoardView - show()")
        pass

    def close(self):
        print("FakeReferenceBoardView - show()")
        pass


@TestFunction
def refBoard_from_json_ok():
    json_board = test_data["json_refboard"]
    json = json_board.replace(" ", "")
    try:
        board = ReferenceBoardModel.model_validate_json(json_board)
    except ValidationError as e:
        print(f"Test Failed: {e}")
        raise TestFailedException()


@TestFunction
def refBoard_from_file_ok():
    ReferenceBoardView = FakeReferenceBoardView
    json_board = test_data["json_refboard"]
    file_name = "test.refboard"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(json_board)
        # print(json_board, file=f)
    try:
        board = ReferenceBoard(file_name)
        assert board._reference_board.board_name == "test", "board name is different"
        # print(f"board images: {board._reference_board.reference_images}")
        for name, image in board._reference_board.reference_images.items():
            assert name in ["pippo", "pluto"], f"name {name} not in [pippo, pluto]"
            # print(f'image "{name}": {image}')
        os.remove(file_name)

    except ValidationError as e:
        print(f"Build form JSON Failed: {e}")
        raise TestFailedException()
    except AssertionError as e:
        print(f"Assertion Failed: {e}")
        raise TestFailedException()


@TestFunction
def refBoard_default():
    ReferenceBoardView = FakeReferenceBoardView
    try:
        board = ReferenceBoard()
        assert board._reference_board.board_name == "unknown", "board name is different"
        # print(f"board images: {board._reference_board.reference_images}")
        num_images = len(board._reference_board.reference_images)
        assert num_images == 0, (
            f"Expected 0 images found  {num_images} \n(debug: {board._reference_board.reference_images})"
        )
    except AssertionError as e:
        print(f"Assertion Failed: {e}")
        raise TestFailedException()


if __name__ == "__main__":
    test_list = [
        refBoard_from_json_ok,
        refBoard_from_file_ok,
        refBoard_default,
    ]

    p, f = RunTest(test_list)
    exit(f)
