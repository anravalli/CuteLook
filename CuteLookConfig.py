from pathlib import Path

from pydantic import BaseModel  # , ValidationError
from UnitTesting import RunTest


class BoardViewState(BaseModel):
    maximized: bool = False
    position: dict[str, int] = None
    size: dict[str, int] = None
    screen: str = "HDMI-1"

    def __init__():
        super().__init__()
        self.position = {"x": 100, "y": 100}
        self.size = {"w": 800, "h": 600}


class RefBoard(BaseModel):
    index: int = 0
    path: Path = Path("~/unknown.refboard")
    view_state: BoardViewState = None

    def __init__():
        super().__init__()
        self.view_state = BoardViewState()


class CuteLookConfig(BaseModel):
    recent_boards: list[RefBoard] = []
    restore_view: bool = True
    max_recent_boards: int = 10


if __name__ == "__main__":
    test_list = []

    p, f = RunTest(test_list)
    exit(f)
