# waydotool
A Python automation toolkit for Wayland, built on `ydotool` and `kdotool`.

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
$ gh repo clone uukelele/waydotool
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
```