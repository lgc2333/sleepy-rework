from enum import StrEnum, auto


class DeviceType(StrEnum):
    PC = auto()
    LAPTOP = auto()
    PHONE = auto()
    TABLET = auto()
    SMARTWATCH = auto()
    UNKNOWN = auto()


class DeviceOS(StrEnum):
    WINDOWS = "Windows"
    MACOS = "MacOS"
    LINUX = "Linux"
    ANDROID = "Android"
    IOS = "iOS"
    UNKNOWN = auto()


class OnlineStatus(StrEnum):
    ONLINE = auto()
    OFFLINE = auto()
    IDLE = auto()
    UNKNOWN = auto()
