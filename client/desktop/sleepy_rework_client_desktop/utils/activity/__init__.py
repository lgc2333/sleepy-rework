import platform

from .base import BaseActivityDetector

ActivityDetector: type[BaseActivityDetector] | None

if platform.system() == "Windows":
    from .windows import WindowsActivityDetector as ActivityDetector
else:
    ActivityDetector = None

activity_detector = None
if ActivityDetector is not None:
    activity_detector = ActivityDetector()

__all__ = ["ActivityDetector", "BaseActivityDetector", "activity_detector"]
