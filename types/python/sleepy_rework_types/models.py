from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, computed_field

from .config import DeviceConfig
from .enums import OnlineStatus


class ErrDetail(BaseModel):
    type: str | None = None
    msg: str | None = None
    data: Any = None


class WSErr(BaseModel):
    code: int
    detail: ErrDetail


class OpSuccess(BaseModel):
    success: Literal[True] = True


class DeviceCurrentApp(BaseModel):
    name: str
    last_change_time: int | None = None


class DeviceData(BaseModel):
    model_config = ConfigDict(extra="allow")

    current_app: DeviceCurrentApp | None = None
    additional_statuses: list[str] | None = None


class DeviceInfoFromClient(DeviceConfig):
    idle: bool = False
    data: DeviceData | None = None


class DeviceInfoFromClientWS(DeviceInfoFromClient):
    replace: bool = False


class DeviceInfo(DeviceInfoFromClient):
    online: bool = False
    last_update_time: int | None = None
    long_connection: bool = False

    @computed_field
    def status(self) -> OnlineStatus:
        if not self.online:
            return OnlineStatus.OFFLINE
        if self.idle:
            return OnlineStatus.IDLE
        return OnlineStatus.ONLINE


class Info(BaseModel):
    status: OnlineStatus
    devices: dict[str, DeviceInfo] | None = None
