from enum import StrEnum, auto


class DeviceType(StrEnum):
    PC = auto()
    LAPTOP = auto()
    PHONE = auto()
    TABLET = auto()
    SMARTWATCH = auto()


class OnlineStatus(StrEnum):
    ONLINE = auto()
    OFFLINE = auto()
    IDLE = auto()
    UNKNOWN = auto()
