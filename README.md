# waydotool
A Python automation toolkit for Wayland, built on `ydotool` and `kdotool`.

## Notes

This is **NOT** a cross-platform replacement for `pyautogui`(or `pygetwindow`). This **ONLY** supports Wayland (for input), and for window management only supports the KWin compositor.

Feel free to contribute things like adding `swayctl` support for the `window` module. Or maybe adding a fallback to `pyautogui`/`pygetwindow` when X11/Windows/Darwin is detected.

## Installation

### Prerequisites

- [`ydotool`](https://github.com/ReimuNotMoe/ydotool) (>=1.0.4) daemon running
- [`kdotool`](https://github.com/jinliu/kdotool) (>= 0.3.0) installed

### Installation

<!-- Uncomment when uploading to PyPI
```
$ pip install waydotool
```
-->

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

## Usage

```python
import waydotool as wd


windows = wd.window.search('Firefox', title=True)

if not windows:
    print("No window found.")
else:
    firefox = windows[0]

    wd.window.activate(firefox)
    wd.input.type('https://github.com/uukelele/waydotool')
```