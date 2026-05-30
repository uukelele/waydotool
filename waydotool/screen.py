import subprocess as sp
import mss
from PIL import Image
from io import BytesIO
from pathlib import Path
from typing import TypedDict, Iterator
import time
import numpy as np

from .utils import get_platform, Platform
from .libs import spectacle

_sc = spectacle.Spectacle()

platform = get_platform()

def screenshot_raw(monitor: int = 0) -> bytes | mss.ScreenShot:
    """
    Takes a screenshot of your screen, and returns a variable type.
    You normally do not need to use this; use `screenshot` instead.

    Args:
        monitor: The monitor ID to use. Default is `0`.

    Returns:
        The image as the native type of the tool that was used to capture it.

    Raises:
        NotImplementedError: If screenshots are not implemented for your platform.
    """
    if platform != Platform.WAYLAND:
        with mss.MSS() as sct:
            sct: mss.MSS

            monitor = sct.monitors[monitor]
            
            shot = sct.grab(monitor)

            return shot
        
    else:
        try:
            proc = sp.run(['grim', '-'], stdout=sp.PIPE, check=True)
            return proc.stdout
        except sp.CalledProcessError: # so, it isn't wlroots
            try:
                return _sc.get_screenshot_bytes()
            except spectacle.SpectacleException:
                raise NotImplementedError("Screenshots are not implemented for your specific Window Manager and compositor.")

def screenshot(monitor: int = 0) -> Image.Image:
    """
    Takes a screenshot of your screen, and returns a PIL.Image.Image

    Args:
        monitor: The monitor ID to use. Default is `0`.

    Returns:
        The image as a PIL.Image.Image you can process.

    Raises:
        NotImplementedError: If screenshots are not implemented for your platform.
    """

    shot = screenshot_raw(monitor=monitor)

    if isinstance(shot, mss.ScreenShot):
        return Image.frombytes('RGB', shot.size, shot.rgb)
    elif isinstance(shot, bytes):
        buf = BytesIO(shot)
        return Image.open(buf)
    
    raise NotImplementedError(f"Parsing screenshots are not supported for type `{type(shot)}`.")

def screenshot_save(filepath: str | Path, monitor: int = 0):
    """
    Takes a screenshot of your screen, and saves it to a set file path.

    Args:
        filepath: The path to save the file to.
        monitor: The monitor ID to use. Default is `0`.

    Raises:
        NotImplementedError: If screenshots are not implemented for your platform.
    """

    shot = screenshot(monitor=monitor)
    path = Path(filepath)

    shot.save(path.resolve())

class Monitor(TypedDict):
    index: int
    left: int
    top: int
    width: int
    height: int
    name: str

def get_monitors(do_not_raise: bool = True) -> list[Monitor]:
    """
    Returns a list of available monitors with their properties.

    Each monitor is a typed dictionary containing the monitor's geometry and name.

    Args:
        do_not_raise: Whether to raise a NotImplementedError if Wayland is detected. Defaults to True, in which case it instead returns an empty list.

    Returns:
        List of monitors.
    """

    if platform == Platform.WAYLAND:
        if do_not_raise: return []
        raise NotImplementedError("Fetching monitors is not supported on Wayland.")
    
    with mss.MSS() as sct:
        sct: mss.MSS
        return [
            {
                'index': i,
                'left': monitor['left'],
                'top': monitor['top'],
                'width': monitor['width'],
                'height': monitor['height'],
                'name': monitor.get('name', f"Monitor {i} ({monitor['width']}x{monitor['height']})")
            } for i, monitor in enumerate(sct.monitors)
            if i != 0 # monitors[0] on mss is the all-in-one monitor
        ]

def stream_raw(
    monitor: int = 0, # ignored on Wayland
    fps: int = 30,
    max_frames: int | None = None,
) -> Iterator[np.ndarray | mss.ScreenShot]:
    """
    Stream screen frames as an iterator of a variable type.
    
    Args:
        monitor: The monitor index to capture. (Ignored on Wayland as monitor is user-selected)
        fps: Frames per second you wish to capture. Actual fps is not guaranteed to remain as high as what you chose.
        max_frames: Maximum number of frames to yield. None means infinite. If you want to record for `x` seconds, use `x * fps` here.

    Yields:
        The image as the native type of the tool that was used to capture it.
    
    Raises:
        NotImplementedError: If the platform is not supported for streaming.
        RuntimeError: If PipeWire capture is not available on your system.
        TimeoutError: If the user takes too long to select a monitor.
    """

    if platform != Platform.WAYLAND:
        interval = 1.0 / fps
        yielded = 0

        with mss.MSS() as sct:
            sct: mss.MSS
            monitor = sct.monitors[monitor]

            while max_frames is None or yielded < max_frames:
                start = time.perf_counter()
                shot = sct.grab(monitor)
                yield shot
                yielded += 1

                elapsed = time.perf_counter() - start
                sleep = interval - elapsed
                if sleep >= 0: time.sleep(sleep)

    else:
        # try:
        #     from pipewire_capture import PortalCapture, CaptureStream, is_available
        # except ImportError as e:
        #     raise ImportError(
        #         "You need to install the `wayland` extra, using `pip install waydotool[wayland]`."
        #     ) from e
        from pipewire_capture import PortalCapture, CaptureStream, is_available

        if not is_available():
            raise RuntimeError("PipeWire capture is not available. Ensure the XDG Desktop Portal is available.")
        
        stream = None
        session = None

        try:
            portal = PortalCapture()

            session = portal.select_window()

            if not session:
                raise RuntimeError("Failed to create Portal capture session.")

            stream = CaptureStream(session.fd, session.node_id, session.width, session.height)
            stream.start()

            interval = 1.0 / fps
            yielded = 0
            last = None

            while max_frames is None or yielded < max_frames:
                start = time.perf_counter()

                frame = stream.get_frame()
                if frame is None:
                    if last is None:
                        time.sleep(interval)
                        continue
                    frame = last
                else:
                    last = frame

                yield frame

                yielded += 1

                elapsed = time.perf_counter() - start
                sleep = interval - elapsed
                if sleep > 0: time.sleep(sleep)

                if stream.window_invalid:
                    raise RuntimeError("The selected window was closed or is no longer available.")
                

        except: raise

        finally:
            if stream: stream.stop()
            if session: session.close()

def stream(
    monitor: int = 0,
    fps: int = 30,
    max_frames: int | None = None,
) -> Iterator[Image.Image]:
    """
    Stream screen frames as an iterator of `PIL.Image.Image`.
    
    Args:
        monitor: The monitor index to capture. (Ignored on Wayland as monitor is user-selected)
        fps: Frames per second you wish to capture. Actual fps is not guaranteed to remain as high as what you chose.
        max_frames: Maximum number of frames to yield. None means infinite. If you want to record for `x` seconds, use `x * fps` here.

    Yields:
        A series of `PIL.Image.Image` images containing each frame.
    
    Raises:
        NotImplementedError: If the platform is not supported for streaming.
        RuntimeError: If PipeWire capture is not available on your system.
        TimeoutError: If the user takes too long to select a monitor.
    """
    for frame in stream_raw(monitor=monitor, fps=fps, max_frames=max_frames):
        if isinstance(frame, mss.ScreenShot):
            yield Image.frombytes('RGB', frame.size, frame.rgb)
        elif isinstance(frame, np.ndarray):
            yield Image.fromarray(frame[:, :, [2, 1, 0]])