from enum import Enum
import platform, os


class Platform(str, Enum):
    WINDOWS = 'windows'
    DARWIN  = 'darwin'
    WAYLAND = 'wayland'
    X11     = 'x11'

def get_platform() -> Platform:
    system = platform.system().lower()

    if system in Platform._value2member_map_:
        return system
    
    session_type = os.getenv("XDG_SESSION_TYPE", "").lower()
    if session_type in Platform._value2member_map_:
        return session_type

    if os.getenv("DISPLAY"):          return 'x11'
    if os.getenv("WAYLAND_DISPLAY"):  return 'wayland'

def kde_version() -> int | None:
    try:
        return int(os.getenv('KDE_SESSION_VERSION'))
    except: return None