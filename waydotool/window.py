# TODO: Write Python-Rust mappings between kdotool and waydotool using maturin
# For now, just reimplement everything using subprocess

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
    x: int
    y: int
    width: int
    height: int

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

        return proc.stdout.strip()
    
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
        Search for windows with titles, names, or classes matching a regular
        expression pattern.

        The default options are --title --class --classname --role (unless you
        specify one or more of --title, --class, --classname, or --role).

        :param pattern: The regular expression pattern to match.
        :param title: Match against the window title. This is the same string that is displayed in the window titlebar.
        :param class_: Match against the window class.
        :param classname: Match against the window classname.
        :param role: Match against the window role.
        :param case_sensitive: Match against the window title case-sensitively.
        :param pid: Match windows that belong to a specific process id. This may not work for some X applications that do not set this metadata on its windows.
        :param desktop: Only match windows on a certain desktop. The default is to search all desktops.
        :param limit: Stop searching after finding NUMBER matching windows. The default is no search limit (which is equivalent to '--limit 0')
        :param match_all: Require that all conditions be met.
        :param match_any: Match windows that match any condition (logically, 'or'). This is on by default.
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
        """
        return self._run(["getactivewindow"])

    def get_mouse_location(self, shell: bool = False) -> str:
        """
        Outputs the x, y, screen, and window id of the mouse cursor.

        :param shell: output shell data you can eval.
        """
        args = ["getmouselocation"]
        if shell: args.append("--shell")
        return self._run(args)

    # Window Action Commands:

    def get_window_name(self, window: WindowID = "%1") -> str:
        """
        Output the name of a window. This is the same string that is displayed
        in the window titlebar.

        :param window: The window to target.
        """
        return self._run(["getwindowname", window])

    def get_window_class_name(self, window: WindowID = "%1") -> str:
        """
        Output the class name of a window.

        :param window: The window to target.
        """
        return self._run(["getwindowclassname", window])

    def get_window_geometry(self, window: WindowID = "%1") -> WindowGeometry:
        """
        Output the geometry (location and position) of a window. The values
        include: x, y, width, height.

        :param window: The window to target.
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

        :param window: The window to target.
        """
        return self._run(["getwindowid", window])

    def get_window_pid(self, window: WindowID = "%1") -> str:
        """
        Output the PID owning a window. This requires effort from the
        application owning a window and may not work for all windows.

        :param window: The window to target.
        """
        return self._run(["getwindowpid", window])

    def window_activate(self, window: WindowID = "%1"):
        """
        Activate a window. If the window is on another desktop, we will switch
        to that desktop.

        :param window: The window to target.
        """
        self._run(["windowactivate", window])

    def window_raise(self, window: WindowID = "%1"):
        """
        Raise a window to the top of the window stack. (KDE 6 only)

        :param window: The window to target.
        """
        self._run(["windowraise", window])

    def window_minimize(self, window: WindowID = "%1"):
        """
        Minimize a window.

        :param window: The window to target.
        """
        self._run(["windowminimize", window])

    def window_close(self, window: WindowID = "%1"):
        """
        Close a window.

        :param window: The window to target.
        """
        self._run(["windowclose", window])

    def window_size(self, width: Union[int, str], height: Union[int, str], window: WindowID = "%1"):
        """
        Resize a window. Percentages are valid for WIDTH and HEIGHT. They are
        relative to the geometry of the screen the window is on.

        If the given WIDTH is literally 'x', then the window's current width
        will be unchanged. The same applies for 'y' for HEIGHT.

        :param window: The window to target.
        :param width: New width.
        :param height: New height.
        """
        self._run(["windowsize", window, str(width), str(height)])

    def window_move(self, x: Union[int, str], y: Union[int, str], window: WindowID = "%1", relative: bool = False):
        """
        Move a window. Percentages are valid for X and Y. They are relative to
        the geometry of the screen the window is on.

        If the given x coordinate is literally 'x', then the window's current
        x position will be unchanged. The same applies for 'y'.

        :param x: New x coordinate.
        :param y: New y coordinate.
        :param window: The window to target.
        :param relative: Make movement relative to the current window position.
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

        NOTE: You can specify multiple --add, --remove, and --toggle options in a
        single command. For example, you can do:
          kdotool windowstate --add above --remove below --toggle skip_taskbar

        :param window: The window to target.
        :param add: show window above all others (always on top), etc.
        :param remove: remove property.
        :param toggle: toggle property.
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

        :param window: The window to target.
        """
        return self._run(["get_desktop_for_window", window])

    def set_desktop_for_window(self, number: Union[int, str], window: WindowID = "%1"):
        """
        Move a window to a different desktop.
        Specify the desktop number or "current_desktop" or "all".

        :param window: The window to target.
        :param number: The desktop number or "current_desktop" or "all".
        """
        self._run(["set_desktop_for_window", window, str(number)])

    # Global Commands:

    def get_desktop(self) -> str:
        """
        Output the current desktop number.
        """
        return self._run(["get_desktop"])

    def set_desktop(self, number: int):
        """
        Change the current desktop to <number>.

        :param number: The desktop number.
        """
        self._run(["set_desktop", str(number)])

    def get_num_desktops(self) -> str:
        """
        Output the current number of desktops.
        """
        return self._run(["get_num_desktops"])
    
_kd = Kdotool()

search = _kd.search
get_active = _kd.get_active_window
get_mouse_location = _kd.get_mouse_location
get_name = _kd.get_window_name
get_class_name = _kd.get_window_class_name
get_geometry = _kd.get_window_geometry
get_id = _kd.get_window_id
get_pid = _kd.get_window_pid
activate = _kd.window_activate
raise_ = _kd.window_raise
minimize = _kd.window_minimize
close = _kd.window_close
size = _kd.window_size
move = _kd.window_move
state = _kd.window_state
get_desktop_for_window = _kd.get_desktop_for_window
set_desktop_for_window = _kd.set_desktop_for_window
get_desktop = _kd.get_desktop
set_desktop = _kd.set_desktop
get_num_desktops = _kd.get_num_desktops