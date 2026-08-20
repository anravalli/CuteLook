# Architecture

This document describes the current source structure of CuteLook.

CuteLook is a PyQt5 desktop application organized around a small manager/controller
layer, Pydantic models used for serialization, Qt views/widgets, and a package of
custom widgets used by floating reference images.

## Source Layout

```text
CuteLook.py                 Application entry point and board manager
ReferenceBoard.py           Board controller
ReferenceBoardView.py       Board main window and QGraphicsView
ReferenceImageView.py       Floating image widget and image interaction logic
ReferenceBoardModels.py     Pydantic board/image models saved to .refboard files
CuteLookConfig.py           Pydantic user configuration and recent board state
CustomWidgets/              Reusable widgets for image controls and editing
```

## Application And Board



```plantuml
@startuml
skinparam classAttributeIconSize 0

class CuteLook {
  - _boards: dict[int, ReferenceBoard]
  - _app_config: CuteLookConfig
  - _app_config_path: Path
  - _next_board_id: int
  + openBoard(board_path: str)
  + closeBoard(board_id: int)
  + boardFactory(path: str)
  + loadConfig()
  + updateConfigFile()
  + addBoardToRecent(board: ReferenceBoard)
}

class ReferenceBoard {
  - _board_id: int
  - _reference_board: ReferenceBoardModel
  - _board_window: ReferenceBoardView
  - _board_path: Path
  - _modified: bool
  - _is_new: bool
  - _z_stack: dict[int, str]
  - _selected_images: list[str]
  + addNewImage(image_path: Path)
  + imageChanged(img_name: str, state: FloatingImageState)
  + save(change_name: bool)
  + getViewState(): BoardViewState
  + restoreViewState(view_state: BoardViewState)
}

class ReferenceBoardView
class ReferenceBoardModel
class CuteLookConfig
class BoardViewState

CuteLook "1" o-- "0..*" ReferenceBoard : owns open boards
CuteLook "1" *-- "1" CuteLookConfig : user config
ReferenceBoard "1" *-- "1" ReferenceBoardModel : board data
ReferenceBoard "1" *-- "1" ReferenceBoardView : board window
ReferenceBoard ..> BoardViewState : stores/restores window state
CuteLookConfig "1" o-- "0..*" BoardViewState : recent boards state
@enduml
```

`CuteLook` is not a `QObject`; it is a plain Python application manager. It creates
the board model, view, and controller, keeps the currently open boards indexed by a
session-local id, and stores the application configuration through `CuteLookConfig`.

`ReferenceBoard` is the controller for one board. It owns the current
`ReferenceBoardModel`, owns the `ReferenceBoardView`, connects view signals to board
operations, keeps selection state, and maintains the z-order stack used by floating
images.

## Serialization Models

```plantuml
@startuml
skinparam classAttributeIconSize 0

class ReferenceBoardModel <<Pydantic BaseModel>> {
  + board_name: str
  + reference_images: dict[str, ReferenceImageModel]
}

class ReferenceImageModel <<Pydantic BaseModel>> {
  + path: str
  + z_order: int
  + scale: float
  + pixmap_offset: dict[str, int]
  + view_size: dict[str, int]
  + view_position: dict[str, int]
  + view_hidden: bool
}

class CuteLookConfig <<Pydantic BaseModel>> {
  + recent_boards: list[RefBoard]
  + restore_view: bool
  + max_recent_boards: int
}

class RefBoard <<Pydantic BaseModel>> {
  + path: Path
  + view_state: BoardViewState
}

class BoardViewState <<Pydantic BaseModel>> {
  + maximized: bool
  + position: dict[str, int]
  + size: dict[str, int]
  + screen: str
}

ReferenceBoardModel "1" *-- "0..*" ReferenceImageModel
CuteLookConfig "1" *-- "0..*" RefBoard
RefBoard "1" *-- "1" BoardViewState
@enduml
```

`ReferenceBoardModel` and `ReferenceImageModel` are serialized into `.refboard`
files. They store the board name and the image-level state needed to restore each
reference image: source path, z-order, content scale, content offset, viewport size,
viewport position, and hidden state.

`CuteLookConfig` is serialized separately in the user configuration directory. It
stores application-level data such as recently opened boards and the saved window
state associated with those recent board entries.

## Board View Package

```plantuml
@startuml
skinparam classAttributeIconSize 0

class ReferenceBoardView extends QMainWindow {
  - _opened_images: dict[str, QGraphicsProxyWidget]
  - _board_actions: dict[str, ReferenceBoardAction]
  - _board_area: BoardGraphicView
  - _board_scene: QGraphicsScene
  - _toolbar: QToolBar
  + addImage(image_name: str, image_model: ReferenceImageModel): FloatingImageWidget
  + closeImage(image_name: str)
  + setImageZvalue(img_name: str, z_order: int)
  + showHideImages()
}

class BoardGraphicView extends QGraphicsView {
  - _scale: float
  - _pan_start_pos: QPoint
  - _ignore_mouse_event: bool
  + ignoreEvents(ignore: bool)
  - _panWithoutScrollbars(drag: QPoint)
}

class ReferenceBoardAction {
  + icon: QIcon
  + action: QAction
  + text: str
  + tooltip: str
}

class QGraphicsScene
class FloatingImageWidget
class ReferenceImageModel

ReferenceBoardView "1" *-- "1" BoardGraphicView
ReferenceBoardView "1" *-- "1" QGraphicsScene
ReferenceBoardView "1" o-- "0..*" ReferenceBoardAction
ReferenceBoardView "1" o-- "0..*" FloatingImageWidget : through scene proxy
ReferenceBoardView ..> ReferenceImageModel
BoardGraphicView ..> QGraphicsScene
@enduml
```

`ReferenceBoardView` is the main window for a board. It creates the toolbar and
context menu actions, owns a `QGraphicsScene`, and displays the scene through
`BoardGraphicView`.

Floating images are added to the scene with `QGraphicsScene.addWidget()`. The view
keeps the returned graphics proxy in `_opened_images` so it can change z-order,
show/hide images, or close them.

`BoardGraphicView` implements board-level zoom and middle-button panning.

## Floating Image View

```plantuml
@startuml
skinparam classAttributeIconSize 0

enum FloatingImageState {
  NORMAL
  HIDDEN
  CLOSED
  ZOOMED
  PANNED
  MOVED
  ZRAISED
  ZLOWERED
  SELECTED
  UNSELECTED
  UPDATED
}

class FloatingImageWidget extends QWidget {
  - _pixmap: QPixmap
  - _pixmap_size: QSize
  - _pixmap_offset: QPoint
  - _image_model: ReferenceImageModel
  - _image_name: str
  - _selected: bool
  + image_state_changed(name: str, state: FloatingImageState)
  + selected(name: str)
  + resizeViewPort(delta_pos: QPoint, delta_size: QSize)
  + updateModel()
  + doClose()
  + doRaise()
  + doLower()
}

class ReferenceImageModel
class FloatingControlButton
class ResizeHandle

FloatingImageWidget "1" o-- "1" ReferenceImageModel
FloatingImageWidget "1" *-- "4" FloatingControlButton : close/hide/raise/lower
FloatingImageWidget "1" *-- "8" ResizeHandle
FloatingImageWidget ..> FloatingImageState
@enduml
```

`FloatingImageWidget` is the actual reference image view. It renders a scaled
`QPixmap`, clips it through the widget viewport, supports image-content panning,
content zoom, viewport resizing, whole-window movement, z-order changes, hide, and
close.

It updates the associated `ReferenceImageModel` whenever position, viewport size, or
pixmap offset changes, then emits `image_state_changed` so `ReferenceBoard` can mark
the board as modified or perform controller-level operations.

## CustomWidgets Package

```plantuml
@startuml
skinparam classAttributeIconSize 0

package CustomWidgets {
  enum FloatingImageButtonTypes {
    CLOSE
    MINIMIZE
    RAISE
    LOWER
  }

  class FloatingControlButton extends QPushButton
  class "FloatingImageButtonFactory()" as FloatingImageButtonFactory <<function>>

  enum ResizeHandleType {
    TopLeft
    TopMiddle
    TopRight
    RightMiddle
    BottomRight
    BottomMiddle
    BottomLeft
    LeftMiddle
  }

  class ResizeHandle extends QWidget {
    - _type: ResizeHandleType
    - _size: int
    - _x_lock: bool
    - _y_lock: bool
    + view_port_resize(delta_pos: QPoint, delta_size: QSize)
  }

  class SelectionBox extends QWidget
  class FloatingLineEdit extends QLineEdit
  class FloatingInputDialog extends QLineEdit
}

FloatingImageButtonFactory ..> FloatingImageButtonTypes
FloatingImageButtonFactory ..> FloatingControlButton
ResizeHandle ..> ResizeHandleType
@enduml
```

`CustomWidgets` contains reusable UI pieces used by the board and floating images:
small floating control buttons, resize handles, the currently experimental
selection box, and inline/floating text inputs.

## Main Signal Flow

```plantuml
@startuml
actor User
participant ReferenceBoardView
participant FloatingImageWidget
participant ReferenceBoard
participant ReferenceBoardModel
participant CuteLook

User -> ReferenceBoardView : toolbar/context action
ReferenceBoardView -> ReferenceBoard : Qt signal\nadd_image/save_board/rename_board
ReferenceBoard -> ReferenceBoardModel : mutate board data
ReferenceBoard -> ReferenceBoardView : update image/window state

User -> FloatingImageWidget : move/resize/zoom/select/close
FloatingImageWidget -> ReferenceBoard : image_state_changed(name, state)
ReferenceBoard -> ReferenceBoardModel : update z-order or remove image
FloatingImageWidget -> ReferenceImageModel : update viewport/offset/position

ReferenceBoardView -> CuteLook : close_board/new_board
CuteLook -> ReferenceBoard : create/close board
CuteLook -> CuteLookConfig : update recent board state
@enduml
```

The application follows a pragmatic Model/View/Controller split:

- Pydantic models define serialized state.
- Qt widgets implement interaction and rendering.
- `ReferenceBoard` coordinates one model/view pair.
- `CuteLook` coordinates application-level lifecycle and configuration.
