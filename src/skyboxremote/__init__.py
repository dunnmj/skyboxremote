"""Sky Remote Library."""

from .skyboxremote import (
    RemoteControl,
    SkyBoxConnectionError,
    ConnectionTimeoutError,
    NotASkyBoxError,
    BOX_MODEL_DEFINITIONS,
)

__all__ = [
    "RemoteControl",
    "SkyBoxConnectionError",
    "ConnectionTimeoutError",
    "NotASkyBoxError",
    "BOX_MODEL_DEFINITIONS",
]

__version__ = "0.0.7"

DEFAULT_PORT = 49160
LEGACY_PORT = 5900  # For use with SkyQ firmware < 060
