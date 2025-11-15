import json
import pathlib

from pydantic import BaseModel, ValidationError
from UnitTesting import *


# Reference Image model
class ReferenceImageModel(BaseModel):
    path: str = ""
    z_order: int = -1
    zoom: float = 1
    image_center: dict[str, float] = {"x": 256, "y": 256}
    view_size: dict[str, float] = {"w": 512, "h": 512}
    view_position: dict[str, float] = {"w": 0, "h": 0}
    view_hidden: bool = False


# Reference Board model and serialization
class ReferenceBoardModel(BaseModel):
    board_name: str = "unknown"
    reference_images: dict[str, ReferenceImageModel] = {}


"""
Unit Tests
"""
test_data = {
    "json_refimage_1": '{"path": "./pippo.png", "zoom": "2"}',
    "json_refimage_2": '{"path": "./pluto.png", "zoom": "1", "image_center": {"x": 256.0, "y": 256.0}, "view_size": {"w": 512.0, "h": 512.0} }',
    "json_refimage_bad": '{"id": "123", "nome": "Alice"}',
    "json_refimage_full": '{"path":"./pippo.png","z_order":-1,"zoom":2.0,"image_center":{"x":256.0,"y":256.0},"view_size":{"w":512.0,"h":512.0},"view_position":{"w":0.0,"h":0.0},"view_hidden":false}',
}


@TestFunction
def refImage_from_json_ok():
    try:
        json_ref = test_data["json_refimage_1"]
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
    try:
        json_ref = test_data["json_refimage_2"]
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
        json_ref = json_ref = test_data["json_refimage_bad"]
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
    test_reference_json = test_data["json_refimage_full"]
    # remove white spaces to avoid errors
    test_reference_json = test_reference_json.replace(" ", "")

    # build RefImage from json text
    json_img = test_data["json_refimage_1"]
    img = ReferenceImageModel.model_validate_json(json_img)

    # check if the RefImage was built as expected
    json_output = img.model_dump_json()
    # print(f"Dumped json ({type(json_output)}):\n {json_output}")
    if test_reference_json != json_output:
        print("ERROR: validated json differs from reference")
        raise TestFailedException()


if __name__ == "__main__":
    test_list = [
        refImage_from_json_ok,
        refImage_from_json2_ok,
        refImage_from_json_failed,
        refImage_to_json_test,
    ]

    p, f = RunTest(test_list)
    exit(f)
