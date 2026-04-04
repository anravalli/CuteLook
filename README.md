<br/>

# CuteLook

A simple application to help artist load and manage their reference images

<br/>

![CuteLook](docs/demo.png)

<br/>

CuteLook goals is to allow the creation of _referece boards_, where artist can load and arrange their reference images with the additional freedom to individually zoom, scale, pan each them individually to select/focus the desired details.
To do that the application offers two modes: _board mode_ and _image mode_.

Board mode:
- Is the default mode within wich you can arrange the images on the board and manage the board itself.
- Main actions available in _board mode_:
    - *add/remove* image to/from the board or temporary *hide* them
    - *move, scale and change Z sorting order* of each image
    - *select* images for edit
    - *open, close, rename, save* boards
    - *zoom, pan* the whole board
 
Image mode:
- While an image is selected, it allow for basic manipulation.
- Available actions:
    - *zoom*: change the image scale without changing the viewport size or shape
    - *crop*: freely change the image viewport size and shape
    - *pan*: move the image inside its viewport
    - *move* and *scale* without getting back to board mode

<br/>

# Install

```bash
$ pip install -r requires.txt
```

<br/>

# Development Status
<br/>

A formal project - with tickets, kanban and all the bells and whistles - has not been opened for this project but the current development status, including implementation roadmap and issues/bugs tracking, con be found in [DevelopmentStatus.md](./docs/DevelopmentStatus.md)

# Architecture
<br/>

To support future developments and anybody who whould eventually use this project to learn coding and software design the application architecture is documented in [Architecture.md](./docs/Architecture.md).
Anyway, beware that this application isn't meant to be a software design reference and I consider to take any possible shortcut in the implementation.

# Notes on AI and generative tools
<br/>
Although 90% of the actual code has been written directly by hand (in the old fashined way :-)), AI generated code has been used the build the intial application prototype (it was about a the board with some floating images). That code has been vastly rewriten but it's steel visible in the initial commits.

AI has been also used as support to quickly grasp libraries API usage and overcome my Python knowledge gap (this is my first more-than-a-script Python project).

