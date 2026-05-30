# TODO: Write Python-Rust mappings between kdotool and waydotool using maturin
# For now, just reimplement everything using subprocess
# Actually we're probably better off just generating JavaScript code and running it via DBus.

import subprocess as sp
from typing import Union, Literal, TypedDict, List, Optional

WindowID = Union[str, Literal['%1', '%@', '%N']]

WindowStateProperty = Literal[
    "ABOVE",
    "BELOW",
    "SKIP_TASKBAR",
    "SKIP_PAGER",
    "FULLSCREEN",
    "SHADED",
    "DEMANDS_ATTENTION",
    "NO_BORDER",
    "MINIMIZED",
    "MAXIMIZED_HORZ",
    "MAXIMIZED_VERT",
    "MAXIMIZED",
]

class WindowGeometry(TypedDict):
    """The geometry of a window, with `x`, `y`, `width`, and `height` values."""

    x: int
    """The `x` position of the window."""

    y: int
    """The `y` position of the window."""

    width: int
    """The width of the window."""

    height: int
    """The height of the window."""

class MouseLocation(TypedDict):

    x: int
    """The `x` position of the mouse."""

    y: int
    """The `y` position of the mouse."""

    screen: str
    """The current screen that the mouse is over."""

    window: str
    """The current window that the mouse is over."""

class KdotoolException(Exception):
    """Raised when kdotool returns a non-zero exit code."""
    exit_code: int
    stderr: str

    def __init__(self, exit_code: int, stderr: str):
        self.exit_code = exit_code
        self.stderr = stderr


class Kdotool:
    __kdotool_version_used__ = '0.3.0'
    
    def __init__(self):
        return
    
    def _run(self, args: List[str]) -> str:

        cmd = ['kdotool', *args]

        proc = sp.run(cmd, capture_output=True, text=True)

        if proc.returncode != 0:
            raise KdotoolException(
                exit_code = proc.returncode,
                stderr = proc.stderr.strip()
            )

        return proc.stdout.strip() or None
    
    # Window Query Commands:

    def search(
        self,
        pattern: str,
        title: bool = False,
        class_: bool = False,
        classname: bool = False,
        role: bool = False,
        case_sensitive: bool = False,
        pid: Optional[int] = None,
        desktop: Optional[int] = None,
        limit: Optional[int] = None,
        match_all: bool = False,
        match_any: bool = False
    ) -> List[WindowID]:
        """
        Searches for windows matching a regular expression pattern.

        The default behavior matches against window title, class, classname,
        and role unless one or more specific criteria are enabled.

        Args:
            pattern: The regular expression pattern to match.
            title: Match against the window title. Defaults to False.
            class_: Match against the window class. Defaults to False.
            classname: Match against the window classname. Defaults to False.
            role: Match against the window role. Defaults to False.
            case_sensitive: Match the pattern case-sensitively. Defaults to False.
            pid: Match windows belonging to a specific process ID. Defaults to None.
            desktop: Only match windows on a specific virtual desktop. Defaults to None.
            limit: Stop searching after finding this number of matching windows.
                Defaults to None (unlimited).
            match_all: Require that all specified conditions be met. Defaults to False.
            match_any: Match windows that meet any specified condition. Defaults to False.

        Returns:
            A list of matching window IDs.
        """
        args = ["search"]
        if case_sensitive: args.append("--case-sensitive")
        if class_: args.append("--class")
        if classname: args.append("--classname")
        if role: args.append("--role")
        if title: args.append("--title")
        if pid is not None: args.extend(["--pid", str(pid)])
        if desktop is not None: args.extend(["--desktop", str(desktop)])
        if limit is not None: args.extend(["--limit", str(limit)])
        if match_all: args.append("--all")
        if match_any: args.append("--any")
        
        args.append(pattern)
        output = self._run(args)
        return output.splitlines() if output else []

    def get_active_window(self) -> WindowID:
        """
        Select the currently active window.

        Returns:
            The active window ID.
        """
        return self._run(["getactivewindow"])

    def get_mouse_location(self) -> MouseLocation:
        """
        Outputs the x, y, screen, and window id of the mouse cursor.

        Returns:
            A dictionary containing `x`, `y`, `screen`, and `window` keys.
        """
        args = ["getmouselocation", "--shell"]
        
        def parse(txt: str) -> MouseLocation:
            if not txt.strip(): return {}
            d = dict(
                l.split('=', 1)
                for l in txt.strip().splitlines()
            )
            return {
                k: int(v) if k in ('X', 'Y') else v
                for k, v in d.items()
            }

        return parse(self._run(args))

    # Window Action Commands:

    def get_window_name(self, window: WindowID = "%1") -> str:
        """
        Output the name of a window. This is the same string that is displayed
        in the window titlebar.

        Args:
            window: The window to target.

        Returns:
            The window title string.
        """
        return self._run(["getwindowname", window])

    def get_window_class_name(self, window: WindowID = "%1") -> str:
        """
        Output the class name of a window.

        Args:
            window: The target window ID. Defaults to "%1".

        Returns:
            The window class name.
        """
        return self._run(["getwindowclassname", window])

    def get_window_geometry(self, window: WindowID = "%1") -> WindowGeometry:
        """
        Output the geometry (location and position) of a window. The values
        include: x, y, width, height.

        Args:
            window: The window to target.

        Returns:
            A dictionary with `x`, `y`, `width`, and `height` keys.
        """
        out = self._run(["getwindowgeometry", window])
        parts = out.replace(',', '').split()
        data = {}
        for i in range(0, len(parts), 2):
            key = parts[i].replace(':', '').lower()
            val = int(parts[i+1])
            data[key] = val
        return WindowGeometry(x=data['x'], y=data['y'], width=data['width'], height=data['height'])

    def get_window_id(self, window: WindowID = "%1") -> str:
        """
        Output the ID of a window.

        Args:
            window: The window to target.

        Returns:
            The window ID.
        """
        return self._run(["getwindowid", window])

    def get_window_pid(self, window: WindowID = "%1") -> str:
        """
        Output the PID owning a window. This requires effort from the
        application owning a window and may not work for all windows.

        Args:
            window: The window to target.

        Returns:
            The PID of the owning process.
        """
        return self._run(["getwindowpid", window])

    def window_activate(self, window: WindowID = "%1"):
        """
        Activate a window. If the window is on another desktop, we will switch
        to that desktop.

        Args:
            window: The window to target.
        """
        self._run(["windowactivate", window])

    def window_raise(self, window: WindowID = "%1"):
        """
        Raise a window to the top of the window stack. (KDE 6 only)

        Args:
            window: The window to target.
        """
        self._run(["windowraise", window])

    def window_minimize(self, window: WindowID = "%1"):
        """
        Minimize a window.

        Args:
            window: The window to target.
        """
        self._run(["windowminimize", window])

    def window_close(self, window: WindowID = "%1"):
        """
        Close a window.

        Args:
            window: The window to target.
        """
        self._run(["windowclose", window])

    def window_size(self, width: Union[int, str], height: Union[int, str], window: WindowID = "%1"):
        """
        Resize a window. Percentages are valid for WIDTH and HEIGHT. They are
        relative to the geometry of the screen the window is on.

        If the given WIDTH is literally 'x', then the window's current width
        will be unchanged. The same applies for 'y' for HEIGHT.

        Args:
            window: The window to target.
            width: New width.
            height: New height.
        """
        self._run(["windowsize", window, str(width), str(height)])

    def window_move(self, x: Union[int, str], y: Union[int, str], window: WindowID = "%1", relative: bool = False):
        """
        Move a window. Percentages are valid for X and Y. They are relative to
        the geometry of the screen the window is on.

        If the given x coordinate is literally 'x', then the window's current
        x position will be unchanged. The same applies for 'y'.

        Args:
            x: New x coordinate.
            y: New y coordinate.
            window: The window to target.
            relative: Make movement relative to the current window position.
        """
        args = ["windowmove"]
        if relative: args.append("--relative")
        args.extend([window, str(x), str(y)])
        self._run(args)

    def window_state(
        self,
        window: WindowID = "%1",
        add: Optional[Union[WindowStateProperty, List[WindowStateProperty]]] = None,
        remove: Optional[Union[WindowStateProperty, List[WindowStateProperty]]] = None,
        toggle: Optional[Union[WindowStateProperty, List[WindowStateProperty]]] = None,
    ):
        """
        Change a property on a window.

        Args:
            window: The window to target.
            add: List of properties to add.
            remove: List of properties to remove.
            toggle: List of properties to toggle.
        """
        args = ["windowstate"]
        
        def process_props(flag, props):
            if not props: return
            if isinstance(props, str): props = [props]
            for p in props:
                args.extend([flag, p])

        process_props("--add", add)
        process_props("--remove", remove)
        process_props("--toggle", toggle)
        args.append(window)
        self._run(args)

    def get_desktop_for_window(self, window: WindowID = "%1") -> str:
        """
        Output the desktop number that a window is on.

        Args:
            window: The window to target.

        Returns:
            The desktop number.
        """
        return self._run(["get_desktop_for_window", window])

    def set_desktop_for_window(self, number: Union[int, str], window: WindowID = "%1"):
        """
        Move a window to a different desktop.
        Specify the desktop number or "current_desktop" or "all".

        Args:
            window: The window to target.
            number: The desktop number or "current_desktop" or "all".
        """
        self._run(["set_desktop_for_window", window, str(number)])

    # Global Commands:

    def get_desktop(self) -> str:
        """
        Output the current desktop number.

        Returns:
            The current desktop number.
        """
        return self._run(["get_desktop"])

    def set_desktop(self, number: int):
        """
        Change the current desktop to <number>.

        Args:
            number: The desktop number.
        """
        self._run(["set_desktop", str(number)])

    def get_num_desktops(self) -> str:
        """
        Output the current number of desktops.

        Returns:
            The current number of desktops.
        """
        return self._run(["get_num_desktops"])