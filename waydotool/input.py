from enum import Enum
from evdev.ecodes import ecodes

from .libs import ydotool, kdotool
from .utils import get_platform, Platform, kde_version

platform = get_platform()

kde = kde_version()

_yd: ydotool.Ydotool | None = None
_kd: kdotool.Kdotool | None = None

if platform == Platform.WAYLAND:
    _yd = ydotool.Ydotool()
else:
    import pyautogui as _pg # Trying to import this on Wayland, even if unused, errors.

if kde and kde >= 6:
    _kd = kdotool.Kdotool()

class MouseButton(Enum):
    """
    Mouse Buttons that you can send click events with.

    0xC0 is left, 0xC1 is right, 0xC2 is middle.
    The rest, you probably don't need to use.
    """

    BTN_0 = 0x00
    BTN_1 = 0x01
    BTN_2 = 0x02
    BTN_3 = 0x03
    BTN_4 = 0x04
    BTN_5 = 0x05
    BTN_6 = 0x06
    BTN_7 = 0x07
    BTN_C0 = 0xC0
    BTN_C1 = 0xC1
    BTN_C2 = 0xC2

class MouseSemantic(Enum):
    """
    Semantic versions of the mouse buttons which you can send click events.
    """
    
    LEFT = "LEFT"
    MIDDLE = "MIDDLE"
    RIGHT = "RIGHT"
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"

SEMANTIC_TO_BUTTON = {
    "LEFT": MouseButton.BTN_C0,
    "MIDDLE": MouseButton.BTN_C2,
    "RIGHT": MouseButton.BTN_C1,
    "PRIMARY": MouseButton.BTN_C0,
    "SECONDARY": MouseButton.BTN_C1,
}

def click(mouse_button: MouseButton | MouseSemantic | str = MouseSemantic.PRIMARY):
    """
    Clicks where the mouse is.

    Args:
        mouse_button: The button you want to click. Can be `LEFT`, `MIDDLE`, `RIGHT`, `PRIMARY`, `SECONDARY`, or a hexadecimal keycode.
    """

    if platform == Platform.WAYLAND:

        if isinstance(mouse_button, MouseSemantic):
            mouse_button = SEMANTIC_TO_BUTTON[mouse_button.value]
        elif isinstance(mouse_button, str):
            mouse_button = SEMANTIC_TO_BUTTON.get(mouse_button.upper(), mouse_button)

        if isinstance(mouse_button, MouseButton):
            button_str = f"{mouse_button.value:02x}"
        else:
            button_str = mouse_button
        return _yd.click(buttons=button_str)
    
    if isinstance(mouse_button, MouseButton):
        mouse_button = MouseSemantic(mouse_button.name)

    return _pg.click(button=mouse_button)

def type(text: str, interval: float = 0.0):
    """
    Type text using the keyboard.

    Args:
        text: The text you want to type.
        interval: The number of seconds between each keypress. Default is 0, so no pause.
    """

    if platform == Platform.WAYLAND:
        return _yd.type(text, key_delay=round(interval * 10000))
    
    return _pg.typewrite(text, interval=interval)

def hotkey(*keys: str, interval: float = 0.0):
    """
    Performs key down presses on the arguments passed in order, then performs key releases in reverse order.

    The effect is that calling hotkey('ctrl', 'shift', 'c') would perform a "Ctrl-Shift-C" hotkey/keyboard shortcut press.

    Args:
        keys: The keys to press, in order.
        interval: The number of seconds between each keypress. Default is 0, so no pause.
    """

    if platform == Platform.WAYLAND:

        def key_to_evdev(key: str) -> int:
            if key.lower() in ('ctrl', 'shift', 'alt'):
                key = f'LEFT{key.upper()}'
            
            return ecodes[f"KEY_{key.upper()}"]
        
        def hotkeys(*keys: str):
            codes = [key_to_evdev(k) for k in keys]
            sq = []
            for c in codes:            sq.append(f"{c}:1")
            for c in reversed(codes):  sq.append(f"{c}:0")
            return ' '.join(sq)


        return _yd.key(hotkeys(*keys), key_delay=round(interval * 1000))
    
    return _pg.hotkey(*keys, interval=interval)

def key(key: str):
    """
    Press a key on the keyboard (e.g. enter).

    Args:
        key: The key you want to press.
    """

    return hotkey([key])

def scroll(dx: int = 0, dy: int = 0):
    """
    Vertically or horizontally scroll the mouse wheel relatively by a certain amount.

    Args:
        dx: The amount to scroll horizontally.
        dy: The amount to scroll vertically.
    """


    if platform == Platform.WAYLAND:
        return _yd.mousemove(dx, dy, wheel=True)

    raise NotImplementedError(f"waydotool does not support moving the mouse wheel on {platform}.")

def move_mouse(x: int, y: int):
    """
    Move the mouse cursor to a point on the screen, absolutely.

    See the `move_mouse_relative` function if you want to use relative positions.

    Args:
        x: X coordinate on the screen.
        y: Y coordinate on the screen.
    """

    if platform == Platform.WAYLAND:
        return _yd.mousemove(x, y, absolute=True)

    return _pg.moveTo(x, y)

def move_mouse_relative(dx: int, dy: int):
    """
    Move the mouse cursor to a point on the screen, relatively.

    See the `move_mouse` function if you want to use absolute positions.

    Args:
        dx: Relative X to the screen width.
        dy: Relative Y to the screen height.
    """
        
    if platform == Platform.WAYLAND:
        return _yd.mousemove(dx, dy, absolute=False)
    
    return _pg.moveRel(dx, dy)

def mouse_position() -> tuple[int, int]:
    """
    Get the current mouse cursor position.

    Returns:
        The mouse position, as `(x, y)`.
    """

    if _kd:
    
        info = _kd.get_mouse_location()

        return int(info['X']), int(info['Y'])

    if platform == Platform.WAYLAND:
        raise NotImplementedError("Wayland users can only query mouse position using KDE Plasma >= 6.")
    
    return _pg.position()