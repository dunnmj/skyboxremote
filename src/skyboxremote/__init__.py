"""Sky Remote Library."""

from .skyboxremote import RemoteControl, SkyBoxConnectionError, ConnectionTimeoutError, NotASkyBoxError

__all__ = [
    "RemoteControl",
    "SkyBoxConnectionError",
    "ConnectionTimeoutError",
    "NotASkyBoxError",
]

__version__ = "0.0.5"

DEFAULT_PORT = 49160
LEGACY_PORT = 5900  # For use with SkyQ firmware < 060
