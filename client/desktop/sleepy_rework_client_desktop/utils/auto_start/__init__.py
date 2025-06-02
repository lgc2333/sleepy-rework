import platform

from .base import BaseAutoStartManager

AutoStartManager: type[BaseAutoStartManager] | None

if platform.system() == "Windows":
    from .windows import WindowsAutoStartManager as AutoStartManager
else:
    AutoStartManager = None

__all__ = ["AutoStartManager"]
