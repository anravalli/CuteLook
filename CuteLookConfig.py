from pathlib import Path

from pydantic import BaseModel  # , ValidationError
from UnitTesting import RunTest


class BoardViewState(BaseModel):
    maximized: bool = False
    zoom_factor: float = 1.0
    scene_center: dict[str, float] = {"x": 0.0, "y": 0.0}
    position: dict[str, int] = {"x": 100, "y": 100}
    size: dict[str, int] = {"w": 800, "h": 600}
    screen: str = "HDMI-1"


class RefBoard(BaseModel):
    # index: int = 0
    path: Path = Path("~/unknown.refboard")
    view_state: BoardViewState = BoardViewState()


class CuteLookConfig(BaseModel):
    recent_boards: list[RefBoard] = []
    restore_view: bool = True
    max_recent_boards: int = 10


if __name__ == "__main__":
    test_list = []

    p, f = RunTest(test_list)
    exit(f)
