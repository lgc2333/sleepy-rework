from enum import StrEnum, auto
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from .config import FrontendStatusConfig, OnlineStatus


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


class DeviceDataOptional(BaseModel):
    model_config = ConfigDict(extra="allow")

    device_type: DeviceType | str | None = None
    device_os: DeviceOS | str | None = None
    current_app: DeviceCurrentApp | None = None


class DeviceInfo(BaseModel):
    name: str
    online: bool = False
    data: DeviceData | None = None
    last_heartbeat_time: int | None = None


class Status(BaseModel):
    type: OnlineStatus
    detail: FrontendStatusConfig


class Info(BaseModel):
    status: Status
    devices: dict[str, DeviceInfo] | None = None


class OpSuccess(BaseModel):
    success: Literal[True] = True
