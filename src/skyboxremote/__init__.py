"""Sky Remote Library."""

from .skyboxremote import RemoteControl, SkyBoxConnectionError, ConnectionTimeoutError, NotASkyBoxError, VALID_KEYS

__all__ = ["RemoteControl", "SkyBoxConnectionError", "ConnectionTimeoutError", "NotASkyBoxError", "VALID_KEYS"]

__version__ = "0.0.6"

DEFAULT_PORT = 49160
LEGACY_PORT = 5900  # For use with SkyQ firmware < 060
