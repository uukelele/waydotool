import evdev
import warnings

def get_devices_with(capability: int) -> list[evdev.InputDevice]:
    devices: list[evdev.InputDevice] = []

    for path in evdev.list_devices():
        try:
            dev = evdev.InputDevice(path)
            caps = dev.capabilities()
            if capability in caps:
                devices.append(dev)
        except Exception:
            continue

    return devices

def get_keyboards() -> list[evdev.InputDevice]: return get_devices_with(evdev.ecodes.EV_KEY)

def listen_for_events(devices: list[evdev.InputDevice]):
    import select

    map = { dev.fd: dev for dev in devices }

    r, w, x = select.select(map.keys(), [], [])

    for fd in r:
        dev = map[fd]
        try:
            for event in dev.read():
                yield event
        except OSError as e:
            if e.errno == 19:
                warnings.warn(f"Device '{dev.name}' disconnected.")
                del map[fd]
                if not map: raise
            else: raise