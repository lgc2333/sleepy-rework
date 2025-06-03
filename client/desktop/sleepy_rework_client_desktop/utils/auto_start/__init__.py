import platform

from .base import BaseAutoStartManager

AutoStartManager: type[BaseAutoStartManager] | None

if platform.system() == "Windows":
    from .windows import WindowsAutoStartManager as AutoStartManager
elif platform.system() == "Darwin":
    from .macos import MacOSAutoStartManager as AutoStartManager
elif platform.system() == "Linux":
    from .linux import LinuxAutoStartManager as AutoStartManager
else:
    AutoStartManager = None

__all__ = ["AutoStartManager"]
