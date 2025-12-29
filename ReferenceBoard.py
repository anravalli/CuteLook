import json
import pathlib

from UnitTesting import *

from ReferenceBoardModels import *
from ReferenceBoardView import *
from CuteLookConfig import BoardViewState


# Reference Board controller
class ReferenceBoard:
    _reference_board: ReferenceBoardModel = None
    _board_window: ReferenceBoardView = None

    _board_path: pathlib.Path = pathlib.Path("./unknown.refboard")
    _modified: bool = False
    _is_new: bool = False
    _disable_event_filter: bool = True
    _next_z: int = 0

    def __init__(
        self,
        board_id: int,
        model: ReferenceBoardModel,
        view: ReferenceBoardView,
        view_state: BoardViewState = None,
    ) -> None:
        # super().__init__()
        self._board_id = board_id
        self._reference_board = model
        self._board_window = view
        self._board_window.setWindowTitle(model.board_name)
        if not view_state == None:
            self.restoreViewState(view_state)

        self._board_window.add_image.connect(self.addNewImage)
        #self._board_window.close_image.connect(self.deleteImage)
        self._board_window.save_board.connect(self.save)
        self._board_window.rename_board.connect(self.renameBoard)

        self.loadRefImages()

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

    def renameBoard(self, new_name):
        if new_name != self._reference_board.board_name:
            self._reference_board.board_name = new_name
            self.updateModifiedStatus(True)

    def save(self, change_name: bool = False) -> None:
        print(f"saving board: {self._reference_board.board_name}")
        print(f"...to: {self._board_path}")

        save_to = self._board_path
        if self._is_new or change_name:
            dirname = self._board_path.resolve().parent
            save_to = (
                str(dirname) + "/" + self._reference_board.board_name + ".refboard"
            )
            save_to = pathlib.Path(self._board_window.openSaveDialog(str(save_to)))
            print(f"(now) saving to: {save_to}")
            if save_to == pathlib.Path(""):
                # abort
                return
            else:
                self._board_path = save_to
                self._modified = True
                self._is_new = False

        # throw if error/fails
        if self._modified:
            # Exceptions will be farwarded to the caller
            print(f"...to: {self._board_path}")
            with open(save_to, "w", encoding="utf-8") as f:
                json_output = self._reference_board.model_dump_json(indent=4)
                f.write(json_output)
            self.updateModifiedStatus(False)

    # need unit test
    def canBeClosed(self) -> bool:
        print(f"Check if board {self._board_id} can be closed")
        close_ok = True
        if self._modified:
            print("board is modified")
            close_ok = self._board_window.confirmClose()
            print(f"close_ok: {close_ok}")
        return close_ok

    def close(self):
        print(f"Closing board {self._board_id}")
        self._board_window.deleteLater()

    def loadRefImages(self) -> None:
        self._next_z = len(self._reference_board.reference_images)
        for image_name, image_model in self._reference_board.reference_images.items():
            # assert image_name not in self._reference_board.reference_images.keys()
            path = pathlib.Path(image_model.path)
            if path.exists() and path.is_file():
                # create view
                new_image = self._board_window.addImage(image_name, image_model)
                # connect to view signals
                new_image.image_state_changed.connect(self.imageChanged)
            else:
                # show warning
                self._board_window.showMissingImageWarning(image_name, image_model.path)

    # need unit test
    def addNewImage(self, image_path: pathlib.Path) -> None:
        # check file path
        if not (image_path.exists() and image_path.is_file()):
            print(f"ERROR: invalid path: {pathlib.Path}")
            raise Exception("invalid path")
        print(f'adding image "{image_path}"')

        # get a valid image name
        image_name = image_path.stem
        i = 1
        while image_name in self._reference_board.reference_images.keys():
            image_name = f"{image_name}-{i}"
            i += 1

        # create the image model and initialize it
        image_model = ReferenceImageModel()
        image_model.path = image_path.absolute().as_posix()
        image_model.z_order = self._next_z
        # create the view
        new_image = self._board_window.addImage(image_name, image_model)
        new_image.image_state_changed.connect(self.imageChanged)

        # add the image to the board and set it to modified
        self._reference_board.reference_images[image_name] = image_model
        self.updateModifiedStatus(True)
        self._next_z += 1
        print(f'added image "{image_name}"')

    # need unit test
    def imageChanged(self, img_name: str, state: FloatingImageState) -> None:
        #print("imageChanged")
        if state == FloatingImageState.HIDDEN:
            self._board_window.setImageHide()
        elif state == FloatingImageState.CLOSED:
            self._board_window.closeImage(img_name)            
            self.deleteImage(img_name)
        #elif state == FloatingImageState.ZCHANGED:
            #self._board_window.updateZorder(img_name)
        else:
            self.updateModifiedStatus(True)
        #print(f'ref board - item in scene: {len(self._board_window._board_scene.items())}')

    # need unit test
    def deleteImage(self, name: str) -> None:
        # exception shall be handled by caller
        del self._reference_board.reference_images[name]
        self.updateModifiedStatus(True)

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

    def getViewState(self) -> BoardViewState:
        print(f'Getting view state for board "{self._board_id}"')
        view_state = BoardViewState()

        size = self._board_window.size()
        view_state.size["w"] = size.width()
        view_state.size["h"] = size.height()
        print(f"...size: {size.width()}x{size.height()}")

        if self._board_window.isMaximized():
            print(f"...is maximized")
            view_state.maximized = True
        else:
            view_state.maximized = False

        pos = self._board_window.pos()
        print(f"...position: {pos.x()}x{pos.y()}")
        view_state.position["x"] = pos.x()
        view_state.position["y"] = pos.y()

        return view_state

    def restoreViewState(self, view_state):
        if view_state.maximized:
            self._board_window.setWindowState(Qt.WindowState.WindowMaximized)
        else:
            self._board_window.setGeometry(
                view_state.position["x"],
                view_state.position["y"],
                view_state.size["w"],
                view_state.size["h"],
            )


import os

test_data = {
    "board_file_name": "./pippo.refboard",
    "json_refboard": '{"board_name": "test",\n\
        "reference_images": \n{ "pippo": \n{"path": "./pippo.png", "scale": "2"}, "pluto": \n{"path": "./pluto.png", "scale": "1", "image_center": {"x": 256.0, "y": 256.0}, "view_size": {"w": 512.0, "h": 512.0}}\n }\n }\n',
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
