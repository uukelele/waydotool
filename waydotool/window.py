from __future__ import annotations
import typing

from .libs import kdotool
from .utils import get_platform, Platform, kde_version

platform = get_platform()

kde = kde_version()

_kd: kdotool.Kdotool | None = None

if platform == Platform.WINDOWS:
    import ctypes as ct

    if typing.TYPE_CHECKING:
        import pygetwindow._pygetwindow_win as _pw
    else:
        import pygetwindow as _pw

if kde and kde >= 6:
    _kd = kdotool.Kdotool()

class Window:
    """
    Basically just a window on your desktop.
    """


    id: str
    _pwWindow: _pw.Win32Window

    def __init__(self, id: str, _pwWindow: _pw.Win32Window | None = None):
        """
        You shouldn't really be constructing a Window yourself, unless you have a really specific need.

        But in case you are:

        Args:
            id: The window ID. For `kdotool` this is a UUID-like ID. For `pygetwindow` it's the window's `hWnd`.
            _pwWindow: (Optional) A reference to the `pygetwindow.Win32Window` object.
        """

        self.id = id
        self._pwWindow = _pwWindow

    @classmethod
    def from_pw(cls, pwWindow: _pw.Win32Window):
        """
        You shouldn't really be using this function yourself, unless you have a really specific need.

        But in case you are:

        This function instantiates a Window from a `pygetwindow.Win32Window` object.
        It finds the _hWnd on the object and sets the class's `id` to it, as well as populating the `_pwWindow` attribute.

        Args:
            pwWindow: The reference to the original `Win32Window`.
        """
        return cls(id=pwWindow._hWnd, _pwWindow=pwWindow)


    @staticmethod
    def search(text: str) -> list[Window]:
        """
        Search windows for a window title.

        Args:
            text: The specific text you are looking for in the window title.

        Returns:
            A list of windows that you can use. Of course, this list could be empty if there are no matches.

        Raises:
            NotImplementedError: If searching windows is not implemented for your platform.
        """

        if _kd:
            return [Window(id) for id in _kd.search(text, title=True)]
        
        if platform == Platform.WINDOWS:
            return [Window.from_pw(w) for w in _pw.getWindowsWithTitle(text)]
        
        raise NotImplementedError(f"Searching windows not implemented for {platform}.")
    
    @staticmethod
    def all() -> list[Window]:
        """
        Returns all open windows.

        Returns:
            A list of windows that you can use. Of course, this list could be empty if there are no opened windows.

        Raises:
            NotImplementedError: If listing windows is not implemented for your platform.
        """
                
        if _kd:
            return [Window(id) for id in _kd.search('')]
        
        if platform == Platform.WINDOWS:
            return [Window.from_pw(w) for w in _pw.getAllWindows()]
        
        raise NotImplementedError(f"Listing windows not implemented for {platform}.")

    @staticmethod
    def active() -> Window:
        """
        Returns the currently focused window.

        Returns:
            A Window object that you can use.

        Raises:
            NotImplementedError: If getting the active window is not implemented for your platform.
        """
                
        if _kd:
            return Window(_kd.get_active_window())

        if platform == Platform.WINDOWS:
            return Window.from_pw(_pw.getActiveWindow())

        raise NotImplementedError(f"Getting active window not implemented for {platform}.")
    
    @property
    def title(self) -> str:
        """
        The title of the window.
        """
                
        if _kd:
            return _kd.get_window_name(self.id)
        
        if platform == Platform.WINDOWS:
            return self._pwWindow.title
        
        raise NotImplementedError(f"Window title not implemented for {platform}.")
        
    @property
    def geometry(self) -> kdotool.WindowGeometry:
        """
        The geometry of a window.

        It's a typed dictionary with `height`, `width`, `x`, and `y` values.
        """

        if _kd:
            return _kd.get_window_geometry(self.id)
        
        if platform == Platform.WINDOWS:
            rect = self._pwWindow._getWindowRect()
            if not rect: return None
            x, y, right, bottom = rect
            width = right - x
            height = bottom - y

            return {
                "height": height,
                "width": width,
                "x": x,
                "y": y,
            }
        
        raise NotImplementedError(f"Window geometry not implemented for {platform}.")
    
    @property
    def height(self) -> int:
        """The height of the window."""
        return self.geometry["height"]

    @property
    def width(self) -> int:
        """The width of the window."""
        return self.geometry["width"]

    @property
    def x(self) -> int:
        """The `x` position of the window."""
        return self.geometry["x"]

    @property
    def y(self) -> int:
        """The `y` position of the window."""
        return self.geometry["y"]

    def activate(self):
        """
        Activate this window, and raise it to the foreground.

        Raises:
            NotImplementedError: If activating windows is not implemented for your platform.
        """
        
        if _kd:
            return _kd.window_activate(self.id)

        if platform == Platform.WINDOWS:
            return self._pwWindow.activate()

        raise NotImplementedError(f"Activating windows not implemented for {platform}.")
    
    def minimize(self):
        """
        Minimize this window.

        Raises:
            NotImplementedError: If minimizing windows is not implemented for your platform.
        """

        if _kd:
            return _kd.window_minimize(self.id)

        if platform == Platform.WINDOWS:
            return self._pwWindow.minimize()
        
        raise NotImplementedError(f"Minimizing windows not implemented for {platform}.")
        
    def maximise(self):
        """
        Maximize this window.

        Raises:
            NotImplementedError: If maximizing windows is not implemented for your platform.
        """
        if _kd:
            return _kd.window_state(self.id, add=kdotool.WindowStateProperty['MAXIMIZED'])

        if platform == Platform.WINDOWS:
            return self._pwWindow.maximize()
        
        raise NotImplementedError(f"Minimizing windows not implemented for {platform}.")
    
    def fullscreen(self):
        """
        Fullscreen this window.

        Raises:
            NotImplementedError: If fullscreening windows is not implemented for your platform.
        """

        if _kd:
            return _kd.window_state(self.id, add=kdotool.WindowStateProperty['FULLSCREEN'])
        
        raise NotImplementedError(f"Fullscreening windows not implemented for {platform}.")

    def close(self):
        """
        Close this window.

        Raises:
            NotImplementedError: If closing windows is not implemented for your platform.
        """
        if _kd:
            return _kd.window_close(self.id)

        if platform == Platform.WINDOWS:
            return self._pwWindow.close()
        
        raise NotImplementedError(f"Closing windows not implemented for {platform}.")
    
    def resize(self, width: float, height: float, relative: bool = False):
        """
        Resize this window.

        Args:
            width: The new width of the window, or the relative width you want to use (e.g. 0.4 -> 40% of the current width, or a constant like 320px).
            height: The new height of the window, or the relative height you want to use (e.g. 0.6 -> 60% of the current height, or a constant like 480px).

        Raises:
            NotImplementedError: If resizing windows is not implemented for your platform.
        """
        if _kd:
            if relative:
                width = f"{width*100}%"
                height = f"{height*100}%"
            return _kd.window_size(width, height, self.id)
        
        if platform == Platform.WINDOWS:
            if relative:
                return self._pwWindow.resizeRel(width, height)
            else:
                return self._pwWindow.resizeTo(width, height)
        
        raise NotImplementedError(f"Resizing windows not implemented for {platform}.")

    def move(self, x: float, y: float, relative: bool = False):
        """
        Move this window.

        Args:
            x: The new `x` position of the window, or the relative `x` you want to use (e.g. 0.4 -> 40% of the current `x`, or a constant like 320px).
            y: The new `y` height of the window, or the relative `y` you want to use (e.g. 0.6 -> 60% of the current `y`, or a constant like 480px).

        Raises:
            NotImplementedError: If moving windows is not implemented for your platform.
        """

        if _kd:
            if relative:
                x = f"{x*100}%"
                y = f"{y*100}%"
            return _kd.window_move(x, y, relative=relative)
        
        if platform == Platform.WINDOWS:
            if relative:
                return self._pwWindow.moveRel(x, y)
            else:
                return self._pwWindow.moveTo(x, y)
        
        raise NotImplementedError(f"Moving windows not implemented for {platform}.")