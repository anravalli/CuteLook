
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
- [x] improvwe save and save-as feature with file name suggestions based on board name
- [x] update board model when an image is scaled or moved
- [x] when selected, images are temporary moved to foregraund 
- [x] images Z-order can be changed using the designed controll buttons 
- [x] images Z-order shall be saved into board file and restored on load
- [x] enter "edit mode"/"image selection" with double click
- [x] all control buttons and resize handles shall be visible when in edit mode
- [x] mouse wheel rotation over an image while in edit mode scale only the content
- [x] mouse wheel rotation over an image while pressing "control" in board mode, scales the whole image window
- [x] mouse wheel rotation over the board or image while in board mode, zoom in/out the whole board
- [x] pressing mouse middle over the board or image while in board mode pan the the whole board
- [x] dragging the maouse while in edit mode shall pan image (content)
- [x] dragging the resize handles will change size/shape of the image view port whitout affecting the content
- [x] the image view port shall never show empty spaces
- [x] store current panning and view port size into model, board file, and restore on load
- [x] board window position, size and state shall be stored into board file and restored on load

### Version 0.9.1
Goals: refinement over 0.9 with some optional features.

Status:
- [ ] store board view zoom and center to file and restore it on load
- [ ] add "fit to window" and "1:1" buttons to board toolbar
- [ ] add a proper build/packging infrastructure to ease app distribution


### Version 1.0
Goals: UI and UX improvement
- [ ] prepare an UI mockup
- [ ] colored selection box around the selected image
- [ ] move control buttons to a dedicated custom toolbar above the image window
- [ ] add a "grip" handle to control toolbar to move the image window while in edit mode 
- [ ] selection box and control toolbar shall be allways visible in forground, on to of any image
- [ ] change mouse shape according to the current action (dragging, resizing, etc.)
- [ ] redesign the resize handles
- [ ] implement a "recently opened boards" list and make it available through the file menu
- [ ] poster tool: generate a variable resolution image of the board (all the images stiched together)
- [ ] add native Windows support add 

### Future Releases (2.0)
Goal: move forward from a "decent" app for managing reference images to something richer and usefull for the users.

Below are reported a few improvements ideas.
<br/>

#### FEAT-01: RefImageClip (subclass of RefImage)
   A "Clip" allows to separatelly display image details
   A Clip is made by copying on the fly an area of the original image and will stay linked to it
   The diplayed area can be can be moved, zoommed and resized but not panned (it will stay centered to the selection)

   ClipView: The clip view is a sub class of the RefImage view
       Additionally, hovering the ClipView a line linking the clip center to the center of the clipped image is displayed
<br/>
#### FEAT-02: Text Annotation
   Allows adding small text note linked to an image's specific point/area.
   Hovering the TextNote the link shall be rendered as line starting from the closest note's corner to the center of the annoted area on the image.
<br/>
#### FEAT-03: Magnified Color Picker
   Generate on the fly a temporary, magnified, fixed size clip, annotated with the current pixel-under-the-mouse color.
   - the clip view moves altougether with the pointer and repositioned to stay always inside the board view
   - while the magnification level is fixed, moving the mouse wheel the smoothing factor (number of adiacent pixels used to determine the picked color) is changed
   - (optional) consider using edge-detection to avoid considering pixels non related to the pixel under the pointer
   - left click will copy the current color to clipboard as RGB hex text
<br/>
#### FEAT-04: ColorSwatch
   A note with an embedded table used to store colors selected from an image.
   Color table:
   * every row store a color with: the actual rendered color, the the RGB hex text, a free text note (e.g. to store a name)
   * every time a coloer is selected a new row is added
   * copying a row will copy the RGB text to the clipboard
   * pasting is not supported
   * selecting a row allow for:
     * deletion by pressing "delete" or "backspace"
     * edit the description field by clicking in it
     * edit the color by selecting a new one on the image
   Adding colors (no row is selected or available in the color table):
   * a new row is temporary created on the table
   * the new temporary row shows in real-time the color of thecurrent pixel under the picker
     * a small, fixed, smooting/de-noising factor applied to help user select the right color
   * on mouse left-click on the image will "save" the temporary row and a new one is created
   * the temporary row is deleted if the mouse is moved outside the image (including moving over the note)
   * a new temporary row is created if the mouse is moved over the image while the note is selected
<br/>
#### FEAT-05: AutoColorSwatch
   A color swatch note auto-generated from an image clip (a rectagular selection).
<br/>


-------------------

# KNOWN ISSUES and BUGS

- [x] crash on context menu open after closing a board
- [x] crash when changing Z order after an immage is closed
- [x] with N boards, after closing board N-1, every new board replace the old one
- [x] context menu is wrongly placed
- [x] crash on "deselect" after an immage is closed
- [ ] resize handles capture "click" events outside the "drawn" handle area
- [ ] sometimes entering image-edit mode couse the image alignment to view bottom right

