import json
import pathlib

from pydantic import BaseModel, ValidationError
from UnitTesting import *


# Reference Image model
class ReferenceImageModel(BaseModel):
    path: str
    z_order: int = -1
    zoom: float = 1
    image_center: dict[str, float] = {"x": 256, "y": 256}
    view_size: dict[str, float] = {"w": 512, "h": 512}
    view_position: dict[str, float] = {"w": 0, "h": 0}
    view_hidden: bool = False

    def fromPath(self, path: pathlib.Path) -> None:
        print("RefImage.fromPath")
        self.path = path.absolute().as_posix()


# Reference Board model and serialization
class ReferenceBoardModel(BaseModel):
    board_name: str
    reference_images: dict[str, ReferenceImageModel]


# Reference Board controller
class ReferenceBoard:
    _reference_board: ReferenceBoardModel
    _board_path: pathlib.Path
    _modified: bool = False

    def __init__(self, board: pathlib.Path) -> None:
        with open(_board_path, "w", encoding="utf-8") as f:
            json_board = f.readall()
            print(f'DEBUG: json_board: \n {json_board}')
            board = ReferenceBoardModel.model_validate_json(json_board)

    def save(self) -> None:
        # throw if error/fails
        if self._modified:
            # Exceptions will be farwarded to the caller
            with open(_board_path, "w", encoding="utf-8") as f:
                json_output = _reference_board.model_dump_json(indent=4)
                f.write(json_output)
            self._modified = False

    def saveAs(self, new_path: pathlib.Path) -> None:
        # throw if error/fails
        self._board_path = new_path
        self.save()

    def close(self) -> None:
        if self._modified:
            # throw AssertionError()
            print("WARNING: file modified")
        # cehck also if file exist

    def addImage(self, new_image: ReferenceImageModel):
        # self.name = path.stem
        self.ref_images.append(new_image)
        self.modified = True

    def deleteImage(self, name):
        #exception shall be handled by caller
        del self._reference_board.reference_images[name]

    def rename(new_name: str):
        self.board_name = new_name
        self.modified = True

    def renameImage(self, old_name: str, new_name: str) -> None:
        #check if the new name is the same as the old one
        return if old_name == new_name

        #check if the new name is already in use
        return if new_name in self._reference_board.reference_images.keys() #consider throwing a proper exception

        #do rename (exception shall be handled by caller)
        refImage = self._reference_board.reference_images.pop(old_name, None)
        self._reference_board.reference_images[new_name] = refImage
        self.modified = True



"""
Unit Tests
"""


@TestFunction
def refImage_from_json_ok():
    # print("\n########## start refImage_test ###########\n")
    path = pathlib.Path("./pippo.txt")
    try:
        json_ref = '{"path": "./pippo.txt", "zoom": "2"}'
        img = ReferenceImageModel.model_validate_json(json_ref)

        # print(f"img {img}")

    except ValidationError as e:
        print(f"Test Failed: {e}")
        raise TestFailedException()
    except TypeError as e:
        print(f"Test Failed: {e}")
        raise TestFailedException()
    except AttributeError as e:
        print(f"ERROR: {e}")
        raise TestFailedException()


@TestFunction
def refImage_from_json2_ok():
    # print("\n########## start refImage_test ###########\n")
    path = pathlib.Path("./pippo.txt")
    try:
        json_ref = '{"path": "./pluto.txt", "zoom": "1", "image_center": {"x": 256.0, "y": 256.0}, "view_size": {"w": 512.0, "h": 512.0} }'
        img = ReferenceImageModel.model_validate_json(json_ref)
    except ValidationError as e:
        print(f"Test Failed: {e}")
        raise TestFailedException()
    except TypeError as e:
        print(f"Test Failed: {e}")
        raise TestFailedException()
    except AttributeError as e:
        print(f"ERROR: {e}")
        raise TestFailedException()


@TestFunction
def refImage_from_json_failed():
    try:
        json_ref = '{"id": "123", "nome": "Alice"}'
        img_2 = ReferenceImageModel.model_validate_json(json_ref)
        # print(f"img_2 {img_2}")
    except TypeError as e:
        print(f"-- ERROR: {e}")
        raise TestFailedException()
    except AttributeError as e:
        print(f"-- ERROR: {e}")
        raise TestFailedException()
    except ValidationError as e:
        print(f"Test Succeded: {e}")


@TestFunction
def refImage_to_json_test():
    test_reference_json = '{\
        "path": "./pippo.txt",\
        "z_order": -1,\
        "zoom": 2.0,\
        "image_center": {"x": 256.0, "y": 256.0},\
        "view_size": {"w": 512.0, "h": 512.0},\
        "view_position": {"w": 0.0, "h": 0.0},\
        "view_hidden": false\
    }'
    # remove white spaces to avoid errors
    test_reference_json = test_reference_json.replace(" ", "")

    # build RefImage from json text
    json_img = '{"path": "./pippo.txt", "zoom": "2"}'
    img = ReferenceImageModel.model_validate_json(json_img)

    # check if the RefImage was built as expected
    json_output = img.model_dump_json()
    # print(f"Dumped json ({type(json_output)}):\n {json_output}")
    if test_reference_json != json_output:
        print("ERROR: validated json differs from reference")
        raise TestFailedException()


@TestFunction
def refBoard_from_json_ok():
    json_board = '{"board_name": "test",\
        "reference_images": { "pippo": {"path": "./pippo.txt", "zoom": "2"}, "pluto": {"path": "./pluto.txt", "zoom": "1", "image_center": {"x": 256.0, "y": 256.0}, "view_size": {"w": 512.0, "h": 512.0} } } }'
    try:
        board = ReferenceBoardModel.model_validate_json(json_board)
    except ValidationError as e:
        print(f"Test Failed: {e}")
        raise TestFailedException()


if __name__ == "__main__":
    test_list = [
        refImage_from_json_ok,
        refImage_from_json2_ok,
        refImage_from_json_failed,
        refImage_to_json_test,
        refBoard_from_json_ok,
    ]

    p, f = RunTest(test_list)
    exit(f)
