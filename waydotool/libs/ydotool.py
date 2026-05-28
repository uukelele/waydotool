# TODO: Write Python-C mappings between ydotool and waydotool
# For now, just reimplement everything using subprocess

import subprocess as sp
import os
from typing import *

MouseButton = Literal[
    "0x00", 0x00,
    "0x01", 0x01,
    "0x02", 0x02,
    "0x03", 0x03,
    "0x04", 0x04,
    "0x05", 0x05,
    "0x06", 0x06,
    "0x07", 0x07,
    "0xC0", 0xC0,
    "0xC1", 0xC1,
    "0xC2", 0xC2,
]

class YdotoolException(Exception):
    """Raised when ydotool returns a non-zero exit code."""
    exit_code: int
    stderr: str

    def __init__(self, exit_code: int, stderr: str):
        self.exit_code = exit_code
        self.stderr = stderr

class Ydotool:
    def __init__(self, socket_path: Optional[str] = None):
        """
        :param socket_path: Optional path to the ydotoold socket. 
                            Defaults to /tmp/.ydotool_socket or environment variable.
        """
        if socket_path:
            os.environ["YDOTOOL_SOCKET"] = socket_path
        return

    def _run(self, args: List[str]) -> str:
        cmd = ['ydotool', *args]
        
        proc = sp.run(cmd, capture_output=True, text=True)

        if proc.returncode != 0:
            raise YdotoolException(
                exit_code=proc.returncode,
                stderr=proc.stderr.strip()
            )

        return proc.stdout.strip()

    def click(
        self,
        buttons: Union[MouseButton, str, List[Union[MouseButton, str]]],
        repeat: Optional[int] = None,
        next_delay: Optional[int] = None,
        press_release: bool = False
    ) -> str:
        """
        Click mouse buttons.

        Options:
          -r, --repeat=N             Repeat entire sequence N times
          -D, --next-delay=N         Delay N milliseconds between input events (up/down,                                a complete click means doubled time)
          -P, --press-release        Press & release mouse button to complete a click, (optional)

        How to specify buttons:
          Now all mouse buttons are represented using hexadecimal numeric values, with an optional
        bit mask to specify if mouse up/down needs to be omitted.
          0x00 - LEFT
          0x01 - RIGHT
          0x02 - MIDDLE
          0x03 - SIDE
          0x04 - EXTR
          0x05 - FORWARD
          0x06 - BACK
          0x07 - TASK
          0x40 - Mouse down
          0x80 - Mouse up
          Examples:
            0x00: chooses left button, but does nothing (you can use this to implement extra sleeps)
            0xC0: left button click (down then up)
            0x41: right button down
            0x82: middle button up
          The '0x' prefix can be omitted if you want.
        """
        args = ["click"]
        if repeat is not None: args.extend(["--repeat", str(repeat)])
        if next_delay is not None: args.extend(["--next-delay", str(next_delay)])
        if press_release: args.append("--press-release")

        buttons = [str(btn) for btn in buttons] if isinstance(buttons, list) else str(buttons)
        
        if isinstance(buttons, list):
            args.extend(buttons)
        else:
            args.append(buttons)
            
        return self._run(args)

    def mousemove(
        self,
        x: int,
        y: int,
        absolute: bool = False,
        wheel: bool = False
    ) -> str:
        """
        Move mouse pointer or wheel.

        Options:
          -w, --wheel                Move mouse wheel relatively
          -a, --absolute             Use absolute position, not applicable to wheel
          -x, --xpos                 X position
          -y, --ypos                 Y position

        You need to disable mouse speed acceleration for correct absolute movement.
        """
        args = ["mousemove"]
        if wheel: args.append("--wheel")
        if absolute: args.append("--absolute")
        
        args.extend(["-x", str(x), "-y", str(y)])
        return self._run(args)

    def type(
        self,
        strings: Union[str, List[str]],
        key_delay: Optional[int] = None,
        key_hold: Optional[int] = None,
        next_delay: Optional[int] = None,
        file: Optional[str] = None,
        escape: Optional[bool] = None
    ) -> str:
        """
        Type strings.

        Options:
          -d, --key-delay=N          Delay N milliseconds between keys (the delay between every key down/up pair) (default: 20)
          -H, --key-hold=N           Hold each key for N milliseconds (the delay between key down and up) (default: 20)
          -D, --next-delay=N         Delay N milliseconds between command line strings (default: 0)
          -f, --file=PATH            Specify a file, the contents of which will be be typed as if passed as an argument.
                                       The filepath may also be '-' to read from stdin
          -e, --escape=BOOL          Escape enable (1) or disable (0)

        Escape is enabled by default when typing command line arguments, and disabled by default when typing from file and stdin.
        """
        args = ["type"]
        if key_delay is not None: args.extend(["--key-delay", str(key_delay)])
        if key_hold is not None: args.extend(["--key-hold", str(key_hold)])
        if next_delay is not None: args.extend(["--next-delay", str(next_delay)])
        if file is not None: args.extend(["--file", file])
        if escape is not None: args.extend(["--escape", "1" if escape else "0"])
        
        if isinstance(strings, list):
            args.extend(strings)
        else:
            args.append(strings)
            
        return self._run(args)

    def key(
        self,
        keycodes: Union[str, List[str]],
        key_delay: Optional[int] = None
    ) -> str:
        """
        Emit key events.

        Options:
          -d, --key-delay=N          Delay N milliseconds between key events

        Since there's no way to know how many keyboard layouts are there in the world,
        we're using raw keycodes now.

        Syntax: <keycode>:<pressed>
        e.g. 28:1 28:0 means pressing on the Enter button on a standard US keyboard.
             (where :1 for pressed means the key is down and then :0 means the key is released)     42:1 38:1 38:0 24:1 24:0 38:1 38:0 42:0 - "LOL"

        Non-interpretable values, such as 0, aaa, l0l, will only cause a delay.

        See `/usr/include/linux/input-event-codes.h' for available key codes (KEY_*).
        """
        args = ["key"]
        if key_delay is not None: args.extend(["--key-delay", str(key_delay)])
        
        if isinstance(keycodes, list):
            args.extend(keycodes)
        else:
            args.append(keycodes)
            
        return self._run(args)

    def debug(self) -> str:
        """
        Internal debug command for ydotool.
        """
        return self._run(["debug"])

    def bakers(self) -> str:
        """
        These are our honorable bakers:

        Dustin Van Tate Testa
        Elliot Wolk
        tofik
        """
        return self._run(["bakers"])