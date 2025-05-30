from enum import StrEnum, auto


class DeviceType(StrEnum):
    PC = auto()
    PHONE = auto()
    TABLET = auto()
    SMARTWATCH = auto()
    UNKNOWN = auto()


class DeviceOS(StrEnum):
    WINDOWS = auto()
    MACOS = auto()
    LINUX = auto()
    ANDROID = auto()
    IOS = auto()
    UNKNOWN = auto()


class OnlineStatus(StrEnum):
    ONLINE = auto()
    OFFLINE = auto()
    IDLE = auto()
    UNKNOWN = auto()
