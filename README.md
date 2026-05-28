# waydotool
A Python automation toolkit that supports Wayland.

Fully typed and has docstrings. Supports Windows, macOS, Linux (X11 / Wayland).

## Warnings

Work on this project is still in progress. Contributions are welcome.

Input mostly works across all platforms, with the exception of scrolling the mouse wheel being **only** supported on Wayland. Additionally, to query the mouse position on Wayland, only KDE Plasma >= 6 is supported. (X11/Windows/macOS is fine).

Managing Windows only works on Windows and KWin (X11 / Wayland) (you must be using KDE Plasma >= 6).

Most of it works across both Windows and KWin, with the exception that fullscreening a window is not yet implemented for Windows (for a hacky fallback, you could try focusing the window then sending the `F11` keycode).

Feel free to contribute things like adding `swayctl` support for the `window` module, or your preferred Window Manager.

And no, this repository wasn't vibe coded. I did have to manually write out all the docstrings (though to be honest there was a fair bit of copying and pasting involved.)

## Installation

### Prerequisites

- **Wayland**
    - [`ydotool`](https://github.com/ReimuNotMoe/ydotool) (>=1.0.4) daemon running
    - **KDE** (>= 6)
        - [`kdotool`](https://github.com/jinliu/kdotool) (>= 0.3.0) installed

If you are not on Wayland, everything should work out-of-the-box.

If you are on Wayland, you will need the `ydotool` daemon installed and running.

If you are on Wayland but not KDE, some features will be missing.

### Installation

```
$ pip install waydotool
```

<!--

```
$ gh repo clone uukelele/waydotool # git clone https://github.com/uukelele/waydotool.git
$ cd waydotool
$ pip install -e .
```

### Updating

```
$ cd waydotool
$ git pull
```
-->

## Usage

```python
from waydotool.window import Window
from waydotool import input
import time


windows = Window.search('Firefox')

if not windows:
    print("No window found.")
else:
    firefox = windows[0]

    firefox.activate()

    time.sleep(1)

    input.type('https://github.com/uukelele/waydotool')

    input.key('enter')
```

There are a lot of exposed functions. They are all documented with docstrings so it should be easy for you to figure out how to use them.