import platform

if platform.system() == "Windows":
    from .windows import WindowsActivityDetector as ActivityDetector
else:
    from .basic import BasicActivityDetector as ActivityDetector

activity_detector = ActivityDetector()
