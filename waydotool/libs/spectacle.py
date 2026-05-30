import subprocess as sp
from typing import Literal, Optional, List, TYPE_CHECKING
import PIL.Image
from io import BytesIO

if TYPE_CHECKING:
    import PIL.Image

RecordMode = Literal[
    "r", "region",
    "s", "screen",
    "w", "window"
]

class SpectacleException(Exception):
    """Raised when spectacle returns a non-zero exit code."""
    exit_code: int
    stderr: str

    def __init__(self, exit_code: int, stderr: str):
        self.exit_code = exit_code
        self.stderr = stderr


class Spectacle:
    def __init__(self):
        pass

    def _run(self, args: List[str], text: bool = True) -> str | bytes:
        cmd = ['spectacle', *args]
        
        proc = sp.run(cmd, capture_output=True, text=text)

        if proc.returncode != 0:
            stderr = proc.stderr if isinstance(proc.stderr, str) else proc.stderr.decode('utf-8', errors='replace')
            raise SpectacleException(
                exit_code=proc.returncode,
                stderr=stderr.strip()
            )

        if text:
            return proc.stdout.strip() if isinstance(proc.stdout, str) else proc.stdout.decode('utf-8', errors='replace').strip()
        return proc.stdout

    def capture(
        self,
        fullscreen: bool = False,
        current: bool = False,
        activewindow: bool = False,
        windowundercursor: bool = False,
        transientonly: bool = False,
        region: bool = False,
        record: Optional[RecordMode] = None,
        launchonly: bool = False,
        gui: bool = False,
        background: bool = False,
        dbus: bool = False,
        nonotify: bool = False,
        output: Optional[str] = None,
        delay: Optional[int] = None,
        copy_image: bool = False,
        copy_path: bool = False,
        onclick: bool = False,
        new_instance: bool = False,
        pointer: bool = False,
        no_decoration: bool = False,
        no_shadow: bool = False,
        edit_existing: Optional[str] = None,
        desktopfile: Optional[str] = None,
    ) -> str | bytes:
        """Executes a screenshot or screen recording capture.

        Args:
            fullscreen: Capture the entire desktop. Defaults to False.
            current: Capture the current monitor. Defaults to False.
            activewindow: Capture the active window. Defaults to False.
            windowundercursor: Capture the window currently under the cursor, 
                including popup menus. Defaults to False.
            transientonly: Capture the window currently under the cursor, 
                excluding popup menus. Defaults to False.
            region: Capture a manually selected rectangular region of the screen. 
                Defaults to False.
            record: Record the screen. Options are 'r'/'region', 's'/'screen', 
                or 'w'/'window'. Defaults to None.
            launchonly: Launch the application without taking a screenshot. 
                Defaults to False.
            gui: Start the application in graphical interface mode. Defaults to False.
            background: Capture a screenshot and exit immediately without 
                displaying the graphical interface. Defaults to False.
            dbus: Start in DBus-Activation mode. Defaults to False.
            nonotify: Prevent notification popups when capturing in background 
                mode. Defaults to False.
            output: Path to save the captured image file. Defaults to None.
            delay: Capture delay in milliseconds in background mode. Defaults to None.
            copy_image: Copy the captured image to the clipboard. Defaults to False.
            copy_path: Copy the saved screenshot file path to the clipboard. 
                Defaults to False.
            onclick: Wait for a mouse click before capturing (invalidates delay). 
                Defaults to False.
            new_instance: Start a new graphical interface instance without 
                DBus registration. Defaults to False.
            pointer: Include the mouse pointer in the capture. Defaults to False.
            no_decoration: Exclude window decorations in the capture. Defaults to False.
            no_shadow: Exclude window drop-shadows in the capture. Defaults to False.
            edit_existing: Path to an existing screenshot file to open and edit. 
                Defaults to None.
            desktopfile: Base file name of the desktop entry. Defaults to None.

        Returns:
            The console output or raw image bytes if outputting to stdout.
        """
        args = []
        if fullscreen: args.append("-f")
        if current: args.append("-m")
        if activewindow: args.append("-a")
        if windowundercursor: args.append("-u")
        if transientonly: args.append("-t")
        if region: args.append("-r")
        if record is not None: args.extend(["-R", record])
        if launchonly: args.append("-l")
        if gui: args.append("-g")
        if background: args.append("-b")
        if dbus: args.append("-s")
        if nonotify: args.append("-n")
        if output is not None: args.extend(["-o", output])
        if delay is not None: args.extend(["-d", str(delay)])
        if copy_image: args.append("-c")
        if copy_path: args.append("-C")
        if onclick: args.append("-w")
        if new_instance: args.append("-i")
        if pointer: args.append("-p")
        if no_decoration: args.append("-e")
        if no_shadow: args.append("-S")
        if edit_existing is not None: args.extend(["-E", edit_existing])
        if desktopfile is not None: args.extend(["--desktopfile", desktopfile])

        text_mode = True
        if output == "/dev/stdout":
            text_mode = False

        return self._run(args, text=text_mode)

    def get_screenshot_bytes(
        self,
        fullscreen: bool = False,
        current: bool = False,
        activewindow: bool = False,
        windowundercursor: bool = False,
        transientonly: bool = False,
        region: bool = False,
        delay: Optional[int] = None,
        pointer: bool = False,
        no_decoration: bool = False,
        no_shadow: bool = False,
    ) -> bytes:
        """
        Capture a screenshot in background mode and return the raw image bytes from stdout.
        
        This sets `--background`, `--nonotify`, and routes the output to `/dev/stdout`.

        Args:
            fullscreen: Capture the entire desktop. Defaults to False.
            current: Capture the current monitor. Defaults to False.
            activewindow: Capture the active window. Defaults to False.
            windowundercursor: Capture the window currently under the cursor, 
                including popup menus. Defaults to False.
            transientonly: Capture the window currently under the cursor, 
                excluding popup menus. Defaults to False.
            region: Capture a manually selected rectangular region of the screen. 
                Defaults to False.
            delay: Capture delay in milliseconds. Defaults to None.
            pointer: Include the mouse pointer in the capture. Defaults to False.
            no_decoration: Exclude window decorations. Defaults to False.
            no_shadow: Exclude window drop-shadows. Defaults to False.

        Returns:
            The raw binary PNG image data.
        """
        result = self.capture(
            fullscreen=fullscreen,
            current=current,
            activewindow=activewindow,
            windowundercursor=windowundercursor,
            transientonly=transientonly,
            region=region,
            background=True,
            nonotify=True,
            output="/dev/stdout",
            delay=delay,
            pointer=pointer,
            no_decoration=no_decoration,
            no_shadow=no_shadow,
        )
        assert isinstance(result, bytes)
        return result

    def get_screenshot_image(
        self,
        fullscreen: bool = False,
        current: bool = False,
        activewindow: bool = False,
        windowundercursor: bool = False,
        transientonly: bool = False,
        region: bool = False,
        delay: Optional[int] = None,
        pointer: bool = False,
        no_decoration: bool = False,
        no_shadow: bool = False,
    ) -> PIL.Image.Image:
        """
        Capture a screenshot in background mode and return it directly as a PIL Image object.
        
        This sets `--background`, `--nonotify`, and routes the output to `/dev/stdout`.

        Args:
            fullscreen: Capture the entire desktop. Defaults to False.
            current: Capture the current monitor. Defaults to False.
            activewindow: Capture the active window. Defaults to False.
            windowundercursor: Capture the window currently under the cursor, 
                including popup menus. Defaults to False.
            transientonly: Capture the window currently under the cursor, 
                excluding popup menus. Defaults to False.
            region: Capture a manually selected rectangular region of the screen. 
                Defaults to False.
            delay: Capture delay in milliseconds. Defaults to None.
            pointer: Include the mouse pointer in the capture. Defaults to False.
            no_decoration: Exclude window decorations. Defaults to False.
            no_shadow: Exclude window drop-shadows. Defaults to False.

        Returns:
            The screenshot image object.
        """

        img_bytes = self.get_screenshot_bytes(
            fullscreen=fullscreen,
            current=current,
            activewindow=activewindow,
            windowundercursor=windowundercursor,
            transientonly=transientonly,
            region=region,
            delay=delay,
            pointer=pointer,
            no_decoration=no_decoration,
            no_shadow=no_shadow,
        )
        return Image.open(BytesIO(img_bytes))

    def get_version(self) -> str:
        """
        Displays version information.
        """
        return self._run(["-v"])

    def get_help(self, all_options: bool = False) -> str:
        """
        Displays help on commandline options.
        If all_options is True, displays help, including generic Qt options.
        """
        args = ["--help-all"] if all_options else ["-h"]
        return self._run(args)

    def get_author(self) -> str:
        """
        Show author information.
        """
        return self._run(["--author"])

    def get_license(self) -> str:
        """
        Show licence information.
        """
        return self._run(["--license"])