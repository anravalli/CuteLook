import pathlib
from pydantic import ValidationError
from PyQt5.QtCore import Qt, QPoint

from UnitTesting import RunTest, TestFunction, TestFailedException

from ReferenceBoardModels import ReferenceBoardModel, ReferenceImageModel
from ReferenceBoardView import ReferenceBoardView
from ReferenceImageView import FloatingImageState
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
    _z_stack: dict[int, str] = None
    _selected_images: list[str] = None

    def __init__(
        self,
        board_id: int,
        model: ReferenceBoardModel,
        view: ReferenceBoardView,
        view_state: BoardViewState = BoardViewState(),
    ) -> None:
        self._z_stack = {}
        self._selected_images = []
        self._board_id = board_id
        self._reference_board = model
        self._board_window = view
        self._board_window.setWindowTitle(model.board_name)

        self.restoreViewState(view_state)

        self._board_window.add_image.connect(self.addNewImage)
        self._board_window.save_board.connect(self.save)
        self._board_window.rename_board.connect(self.renameBoard)
        self._board_window.deselect_images.connect(self.deselectAllImages)

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
        # print(f"...to: {self._board_path}")

        save_to = self._board_path
        if self._is_new or change_name:
            dirname = self._board_path.resolve().parent
            save_to = (
                str(dirname) + "/" + self._reference_board.board_name + ".refboard"
            )
            save_to = pathlib.Path(self._board_window.openSaveDialog(str(save_to)))
            # print(f"(now) saving to: {save_to}")
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
            # print(f"...to: {self._board_path}")
            with open(save_to, "w", encoding="utf-8") as f:
                json_output = self._reference_board.model_dump_json(indent=4)
                f.write(json_output)
            self.updateModifiedStatus(False)

    # need unit test
    def canBeClosed(self) -> bool:
        # print(f"Check if board {self._board_id} can be closed")
        close_ok = True
        if self._modified:
            # print("board is modified")
            close_ok = self._board_window.confirmClose()
            # print(f"close_ok: {close_ok}")
        return close_ok

    def close(self):
        print(f"Closing board {self._board_id}")
        self._board_window.deleteLater()

    def loadRefImages(self) -> None:
        for image_name, image_model in self._reference_board.reference_images.items():
            # assert image_name not in self._reference_board.reference_images.keys()
            path = pathlib.Path(image_model.path)
            if path.exists() and path.is_file():
                # create view
                new_image = self._board_window.addStoredImage(image_name, image_model)
                # connect to view signals
                new_image.image_state_changed.connect(self.imageChanged)
            else:
                # show warning
                self._board_window.showMissingImageWarning(image_name, image_model.path)

            if image_model.z_order < 0:
                image_model.z_order = self._next_z

            self._z_stack[image_model.z_order] = image_name
            self._next_z += 1

        # print(f"next Z: {self._next_z}")

    # need unit test
    def addNewImage(self, images_paths: [str]) -> None:
        default_pos_xy = 50
        initial_pos_multi = 1
        for path in images_paths:
            image_path = pathlib.Path(path)
            # check file path
            if not (image_path.exists() and image_path.is_file()):
                # print(f"ERROR: invalid path: {pathlib.Path}")
                raise Exception("invalid path")
            print(f'adding image "{image_path}"')

            # get a valid image name
            image_name = image_path.stem
            i = 1
            while image_name in self._reference_board.reference_images.keys():
                image_name = f"{image_path.stem}-{i}"
                i += 1

            # create the image model and initialize it
            image_model = ReferenceImageModel()
            image_model.path = image_path.absolute().as_posix()
            image_model.z_order = self._next_z

            # set the default position for new images
            offset = QPoint(default_pos_xy * initial_pos_multi,
                default_pos_xy * initial_pos_multi)

            pos = self._board_window.viewportOffsetToScenePosition(offset)

            image_model.view_position["x"] = pos.x()
            image_model.view_position["y"] = pos.y()

            # needed to correctly set the appearence of new images
            image_model.view_size = None

            self._z_stack[self._next_z] = image_name
            # create the view
            new_image = self._board_window.addNewImage(image_name, image_model)
            new_image.image_state_changed.connect(self.imageChanged)


            # add the image to the board and set it to modified
            self._reference_board.reference_images[image_name] = image_model
            self.updateModifiedStatus(True)
            self._next_z += 1
            # print(f'added image "{image_name}"')
            initial_pos_multi = initial_pos_multi + 1

    # need unit test
    def imageChanged(self, img_name: str, state: FloatingImageState) -> None:
        match state:
            case FloatingImageState.HIDDEN:
                self._board_window.setImageHide()
            case FloatingImageState.CLOSED:
                self.closeImage(img_name)
            case FloatingImageState.SELECTED:
                # print(f"image selected: {img_name}")
                self.checkSelectedImage(img_name)
            case FloatingImageState.UNSELECTED:
                # print(f"image deselect: {img_name}")
                self.checkSelectedImage(img_name, False)
            case FloatingImageState.ZRAISED:
                # print(f"image z raised: {img_name}")
                self.raiseImageZ(img_name)
            case FloatingImageState.ZLOWERED:
                # print(f"image z lowered: {img_name}")
                self.lowerImageZ(img_name)
            case FloatingImageState.MOUSE_ON:
                self._board_window.imgMouseOver(img_name, True)
            case FloatingImageState.MOUSE_OFF:
                self._board_window.imgMouseOver(img_name, False)
            case FloatingImageState.MOUSE_EVENT:
                self._board_window.updateImageHighlightBox(img_name)
            case _:
                self.updateModifiedStatus(True)

    def closeImage(self, img_name: str):
        print(f"closeImage ({img_name})")
        self.removeImageFromSelection(img_name)
        self.__fixZStack(img_name)
        self._board_window.closeImage(img_name)
        self.deleteImage(img_name)

    def __fixZStack(self, img_name):
        # print(f"__fixZStack ({img_name})")
        # get Z of the about to delete image
        z_delete = self._reference_board.reference_images[img_name].z_order
        stack_size = len(self._reference_board.reference_images)
        # z_top = stack_size - 1
        # iterate over the image stacked above the current one
        for img_idx in range(z_delete + 1, stack_size):
            # self._reference_board.reference_images[img_name].z_order -= 1
            # get the image to shift
            img = self._z_stack[img_idx]
            # new index for the image
            new_z_index = img_idx - 1
            # shift down image in the stack
            self._z_stack[new_z_index] = img
            # set the new z order for the image
            self._reference_board.reference_images[img].z_order = new_z_index
            # tell the view that z has changed
            self._board_window.setImageZvalue(img, new_z_index)

        # shirnk the stack
        self._z_stack.pop(z_delete)

    def removeImageFromSelection(self, img_name: str) -> None:
        for img_name in self._selected_images:
            # print(f"deselected image: {img_name}")
            self._selected_images.remove(img_name)
            self._board_window.deselectImages([img_name])

    # NOTE: this appraoch is valid unless multi selection isn't in place
    def checkSelectedImage(self, img_name: str, selected: bool = True) -> None:
        # print(f"selected image: {img_name}")
        if img_name not in self._selected_images:
            # print(f"old selected image: {self._selected_images}")
            self.deselectAllImages()
            if selected:
                self._selected_images.append(img_name)
                self._board_window._board_area.ignoreEvents(True)

    def deselectAllImages(self) -> None:
        self._board_window.deselectImages(self._selected_images)
        self._selected_images.clear()

    def raiseImageZ(self, img_name: str) -> None:
        curr_z = self._reference_board.reference_images[img_name].z_order
        new_z = curr_z + 1
        # print(f"{img_name} zeta order is: {curr_z}")
        if new_z < len(self._z_stack):
            self._reference_board.reference_images[img_name].z_order = new_z
            upper_img = self._z_stack[new_z]
            self._reference_board.reference_images[upper_img].z_order = curr_z
            self._z_stack[new_z] = img_name
            self._z_stack[curr_z] = upper_img
            # print(f"...new zeta order is: {new_z}")
            self._board_window.setImageZvalue(img_name, new_z)
            self._board_window.setImageZvalue(upper_img, curr_z)
            self.updateModifiedStatus(True)

    def lowerImageZ(self, img_name: str) -> None:
        curr_z = self._reference_board.reference_images[img_name].z_order
        new_z = curr_z - 1
        # print(f"{img_name} zeta order is: {curr_z}")
        if new_z >= 0:
            self._reference_board.reference_images[img_name].z_order = new_z
            lower_img = self._z_stack[new_z]
            self._reference_board.reference_images[lower_img].z_order = curr_z
            self._z_stack[new_z] = img_name
            self._z_stack[curr_z] = lower_img
            # print(f"...new zeta order is: {new_z}")
            self._board_window.setImageZvalue(img_name, new_z)
            self._board_window.setImageZvalue(lower_img, curr_z)
            self.updateModifiedStatus(True)

    # need unit test
    def deleteImage(self, name: str) -> None:
        # exception shall be handled by caller
        del self._reference_board.reference_images[name]
        self.updateModifiedStatus(True)

    # need unit test
    def rename(self, new_name: str) -> None:
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
            "Name already in use"
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
        # print(f'Getting view state for board "{self._board_id}"')
        view_state = BoardViewState()

        size = self._board_window.size()
        view_state.size["w"] = size.width()
        view_state.size["h"] = size.height()
        # print(f"...size: {size.width()}x{size.height()}")

        if self._board_window.isMaximized():
            # print("...is maximized")
            view_state.maximized = True
        else:
            view_state.maximized = False

        pos = self._board_window.pos()
        view_state.position["x"] = pos.x()
        view_state.position["y"] = pos.y()

        view_state.zoom_factor = self._board_window.getCurrentViewScale()
        # print("...getSceneCenter")
        scene_center = self._board_window.getSceneCenter()
        # print(f"...scene_center: {scene_center}")
        view_state.scene_center["x"] = scene_center.x()
        view_state.scene_center["y"] = scene_center.y()

        return view_state

    def restoreViewState(self, view_state):
        # print("restoreViewState")
        if view_state.maximized:
            self._board_window.setWindowState(Qt.WindowState.WindowMaximized)
        else:
            self._board_window.setGeometry(
                view_state.position["x"],
                view_state.position["y"],
                view_state.size["w"],
                view_state.size["h"],
            )
        self._board_window.setCurrentViewScale(view_state.zoom_factor)
        # print(f"Restored view ZOOM factor: {self._board_window._board_area._scale}")
        # print(f"restoring scene center to: {view_state.scene_center["x"]}, {view_state.scene_center["y"]}")
        self._board_window.setSceneCenter(view_state.scene_center["x"], view_state.scene_center["y"])


from os import remove

test_data = {
    "board_file_name": "./pippo.refboard",
    "json_refboard": '{"board_name": "test",\n\
        "reference_images": \n{ "pippo": \n{"path": "./pippo.png", "scale": "2"}, "pluto": \n{"path": "./pluto.png", "scale": "1", "image_center": {"x": 256.0, "y": 256.0}, "view_size": {"w": 512.0, "h": 512.0}}\n }\n }\n',
}


class FakeReferenceBoardView:
    def show(self):
        # print("FakeReferenceBoardView - show()")
        pass

    def close(self):
        # print("FakeReferenceBoardView - show()")
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
        remove(file_name)

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
