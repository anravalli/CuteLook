
# Development Status
-------------------

<br/>

## Development Road Map
<br/>

### Version 0.9
Goals: basic features and application core functionalities.

Status:
- [x] add a proper toolbar with icons and actions
- [x] add context menu (right-click)
- [x] store images and their positions into board model 
- [x] multi image selection and loading
- [x] improve save and save-as feature with file name suggestions based on board name
- [x] update board model when an image is scaled or moved
- [x] when selected, images are temporary moved to foreground 
- [x] images Z-order can be changed using the designed control buttons 
- [x] images Z-order shall be saved into board file and restored on load
- [x] enter "edit mode"/"image selection" with double click
- [x] all control buttons and resize handles shall be visible when in edit mode
- [x] mouse wheel rotation over an image while in edit mode scale only the content
- [x] mouse wheel rotation over an image while pressing "control" in board mode, scales the whole image window
- [x] mouse wheel rotation over the board or image while in board mode, zoom in/out the whole board
- [x] pressing mouse middle over the board or image while in board mode pan the whole board
- [x] dragging the mouse while in edit mode shall pan image (content)
- [x] dragging the resize handles will change size/shape of the image view port without affecting the content
- [x] the image view port shall never show empty spaces
- [x] store current panning and view port size into model, board file, and restore on load
- [x] board window position, size and state shall be stored into board file and restored on load

### Version 0.9.1
Goals: refinement over 0.9 with some optional features.

Status:
- [x] store board view zoom and center to file and restore it on load
- [x] add "fit to window" and "1:1" buttons to board toolbar
- [x] newly added images shall be fully visible independently of their size
- [x] add a proper build/packging infrastructure to ease app distribution
- [x] image contour should be highlighted and drawn in foreground on mouse over
- [x] image name shall be displayed at the bottom of the board view (in foreground) on mouse over
- [ ] implement a "recently opened boards" list and make it available through the file menu
- [x] set board name on save

### Version 0.9.9
Goals: Code refactoring and UI consolidation
- [ ] refactoring
- [ ] proper logging infrastructure
- [ ] move control buttons to a dedicated custom toolbar above the image window
- [ ] dragging the image toolbar shall move the image
- [ ] split image interaction in two state:
  - [ ] selected: move, scale, sort (show toolbar)
  - [ ] edit: view port resize, scale, change offset
- [ ] move the view port resize handles away from image view 
- [ ] add help button to toolbox
- [ ] add About screen
- [ ] add help screen


### Version 1.0
Goals: UI and UX improvement and bug fixing
- [ ] add preference windows
- [ ] allow changing icons theme
- [ ] change mouse shape according to the current action (dragging, resizing, etc.)
- [ ] add rotate and flip support 
- [ ] redesign the resize handles
- [ ] poster tool: generate a variable resolution image of the board (all the images stitched together)
- [ ] add native Windows support
- [ ] internationalization

### Future Releases (2.0)
Goal: move forward from a "decent" app for managing reference images to something richer and useful for the users.

Below are reported a few improvements ideas.
<br/>

#### FEAT-01: RefImageClip (subclass of RefImage)
   A "Clip" allows to separately display image details
   A Clip is made by copying on the fly an area of the original image and will stay linked to it
   The displayed area can be moved, zoomed and resized but not panned (it will stay centered to the selection)

   ClipView: The clip view is a subclass of the RefImage view
       Additionally, hovering the ClipView a line linking the clip center to the center of the clipped image is displayed
<br/>
#### FEAT-02: Text Annotation
   Allows adding small text note linked to an image's specific point/area.
   Hovering the TextNote the link shall be rendered as line starting from the closest note's corner to the center of the annotated area on the image.
<br/>
#### FEAT-03: Magnified Color Picker
   Generate on the fly a temporary, magnified, fixed size clip, annotated with the current pixel-under-the-mouse color.
   - the clip view moves altogether with the pointer and repositioned to stay always inside the board view
   - while the magnification level is fixed, moving the mouse wheel the smoothing factor (number of adjacent pixels used to determine the picked color) is changed
   - (optional) consider using edge-detection to avoid considering pixels non related to the pixel under the pointer
   - left click will copy the current color to clipboard as RGB hex text
<br/>
#### FEAT-04: ColorSwatch
   A note with an embedded table used to store colors selected from an image.
   Color table:
   * every row store a color with: the actual rendered color, the the RGB hex text, a free text note (e.g. to store a name)
   * every time a color is selected a new row is added
   * copying a row will copy the RGB text to the clipboard
   * pasting is not supported
   * selecting a row allow for:
     * deletion by pressing "delete" or "backspace"
     * edit the description field by clicking in it
     * edit the color by selecting a new one on the image
   Adding colors (no row is selected or available in the color table):
   * a new row is temporarily created on the table
   * the new temporary row shows in real-time the color of the current pixel under the picker
     * a small, fixed, smooting/de-noising factor applied to help user select the right color
   * on mouse left-click on the image will "save" the temporary row and a new one is created
   * the temporary row is deleted if the mouse is moved outside the image (including moving over the note)
   * a new temporary row is created if the mouse is moved over the image while the note is selected
<br/>
#### FEAT-05: AutoColorSwatch
   A color swatch note auto-generated from an image clip (a rectangular selection).
<br/>


-------------------

# KNOWN ISSUES and BUGS

- [x] crash on context menu open after closing a board
- [x] crash when changing Z order after an immage is closed
- [x] with N boards, after closing board N-1, every new board replace the old one
- [x] context menu is wrongly placed
- [x] crash on "deselect" after an immage is closed
- [ ] resize handles capture "click" events outside the "drawn" handle area
- [ ] sometimes entering image-edit mode cause the image alignment to view bottom right
- [ ] index exception on z change after closing an image
- [ ] highlight box is not aligned to the image while zooming the scene if the view scrolls
- [ ] newly opened images appear misplaced if the board view has not been updated (es. drag, resize, etc.)
- [ ] scene isn't correctly restored when a board is reopened 

