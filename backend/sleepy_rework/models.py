from enum import StrEnum, auto
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from .config import OnlineStatus


class ErrDetail(BaseModel):
    type: str | None = None
    msg: str | None = None
    data: Any = None


class DeviceCurrentApp(BaseModel):
    name: str
    last_change_time: int | None = None


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


class DeviceData(BaseModel):
    model_config = ConfigDict(extra="allow")

    device_type: DeviceType | str = DeviceType.UNKNOWN
    device_os: DeviceOS | str = DeviceOS.UNKNOWN
    current_app: DeviceCurrentApp | None = None


class DeviceInfo(BaseModel):
    name: str
    online: bool = False
    data: DeviceData | None = None
    last_update_time: int | None = None
    long_connection: bool = False


class Info(BaseModel):
    status: OnlineStatus
    devices: dict[str, DeviceInfo] | None = None


class OpSuccess(BaseModel):
    success: Literal[True] = True
