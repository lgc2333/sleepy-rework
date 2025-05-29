from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, computed_field

from .config import DeviceConfig, OnlineStatus


class ErrDetail(BaseModel):
    type: str | None = None
    msg: str | None = None
    data: Any = None


class DeviceCurrentApp(BaseModel):
    name: str
    last_change_time: int | None = None


class DeviceData(BaseModel):
    model_config = ConfigDict(extra="allow")

    current_app: DeviceCurrentApp | None = None
    additional_statuses: list[str] | None = None


class DeviceInfoRecv(DeviceConfig):
    name: str | None = None  # pyright: ignore
    data: DeviceData | None = None
    idle: bool = False


class DeviceInfo(DeviceConfig):
    data: DeviceData | None = None
    idle: bool = False

    online: bool = False
    last_update_time: int | None = None
    long_connection: bool = False

    @computed_field
    def status(self) -> OnlineStatus:
        if self.online:
            return OnlineStatus.ONLINE
        if self.idle:
            return OnlineStatus.IDLE
        return OnlineStatus.OFFLINE


class Info(BaseModel):
    status: OnlineStatus
    devices: dict[str, DeviceInfo] | None = None


class OpSuccess(BaseModel):
    success: Literal[True] = True
