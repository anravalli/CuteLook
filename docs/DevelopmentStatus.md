
# Development Status
-------------------

<br/>

## Development Road Map
<br/>

### Version 0.9
- [ ] enter "edit mode"/"image selection" with double click
- [x] update board model when the image is scaled
- [x] selezione e portare in primo piano con ctrl+left_click
- [x] riposizionare le immagini al caricamento da file
- [x]  Z-order (+ save&restore)
- [ ] centratura su zoom immagini
- [ ] pan immagini (+ save&restore)
- [ ] crop and resize delle immagini (+ save&restore)
- [x] salvare dimensioni e stato della finestra (massimizzata o no)
- [ ] menu "board recenti"
- [ ] verificare che all'apertura di una board le immagini siano sempre visibili sulla canvas
- [x] aggiungere toolbar con icone al posto dei buttons
- [x] aggiungere menu contestuale (right-click)
- [x] multi image open
- [x] migliora save e saveas con suggerimento basato su nome board

### Version 1.0
- [ ] UI cleanup

### Future Releases (2.0)
<br/>

#### FEAT-01: RefImageClip (subclass of RefImage)
   A "Clip" allows to separatelly display image details
   A Clip is made by copying on the fly an area of the original image and will stay linked to it
   The diplayed area can be can be moved, zoommed and resized but not panned (it will stay centered to the selection)

   ClipView: The clip view is a sub class of the RefImage view
       Additionally, hovering the ClipView a line linking the clip center to the center of the clipped image is displayed
<br/>
#### FEAT-02: Text Annotation
   Allows adding small text note Images linked to a specific point in it.
   Hovering the TextNote a line linking the note to the center of the clipped image is displayed
<br/>
#### FEAT-03: ColorSwatch
   Display edit e note with color swatch
<br/>
#### FEAT-04: AutoColorSwatch
   A color swatch note auto-generatare from an image clip.
<br/>
#### FEAT-05: Magnified Color Picker
   Generate on the fly a temporary, magnified, fixed size clip, annotated with the current pixel-unde-the-mouse color.
   - the clip view moves altougether with the pointer and repositioned to stay always inside the main view
   - while the magnification level is fixed, moving the mouse wheel the smoothing factor (number of adiacent pixels used to determine the picked color)
   - (optional) consider using edge-detection to avoid considering pixels non related to the pixel under the pointer


-------------------

# KNOWN ISSUES and BUGS

- [x] crash on context menu open after closing a board
- [x] crash when changing Z order after an immage is closed
- [x] with N boards, after closing board N-1, every new board replace the old one
- [x] context menu is wrongly placed
- [x] crash on "deselect" after an immage is closed
