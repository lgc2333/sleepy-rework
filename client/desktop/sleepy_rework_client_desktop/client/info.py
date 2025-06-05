import json
from typing import Any, Self

from debouncer import DebounceOptions, debounce
from pydantic import BaseModel
from qfluentwidgets import qconfig

from sleepy_rework_types import DeviceInfo, DeviceInfoFromClientWS

from ..config import config
from ..utils.common import SafeLoggedSignal, deep_update
from ..utils.info.shared import (
    get_device_os,
    get_device_type,
    get_initial_device_info_dict,
)
from .base import RetryWSClient

THROTTLE = 1


class DeviceInfoFeeder(RetryWSClient[str]):
    def __init__(
        self,
        endpoint: str,
        secret: str,
        initial_info: DeviceInfoFromClientWS | None = None,
        **kwargs,
    ):
        super().__init__(endpoint, decode=True, **kwargs)

        self.update_secret(secret)
        self.initial_info = initial_info or DeviceInfoFromClientWS()

        self._server_side_info: DeviceInfo | None = None
        self._send_buffer: dict[str, Any] = {}

        self.on_info_update = SafeLoggedSignal[[Self, DeviceInfoFromClientWS], None]()
        self.on_before_send_info = SafeLoggedSignal[[Self, dict[str, Any]], None]()
        self.on_server_side_info_updated = SafeLoggedSignal[[Self, DeviceInfo], None]()

        self.on_connected.connect(lambda _: self._handle_connected())
        self.on_message.connect(lambda _, msg: self._handle_message(msg))
        self.on_info_update.connect(lambda _, x: self._handle_info_update(x))

        @debounce(
            THROTTLE,
            DebounceOptions(leading=True, trailing=True, time_window=THROTTLE),
        )
        async def _debounced_send_buf():
            buf = self._send_buffer
            self._send_buffer = {}
            await self.send_obj(buf)

        self._debounced_send_buf = _debounced_send_buf

    @property
    def server_side_info(self) -> DeviceInfo | None:
        return self._server_side_info

    def update_secret(self, secret: str):
        self.connect_kwargs.setdefault("additional_headers", {})
        self.connect_kwargs["additional_headers"]["Authorization"] = f"Bearer {secret}"

    def update_info(self, info: DeviceInfoFromClientWS | None = None):
        if not info:
            info = DeviceInfoFromClientWS()
        self.on_info_update.task_gather(self, info)

    async def send_obj(self, d: Any):
        self.on_before_send_info.task_gather(self, d)
        await self.ws.send(json.dumps(d))

    async def send_model(self, v: BaseModel):
        return await self.send_obj(v.model_dump(exclude_unset=True))

    async def _handle_connected(self):
        await self.send_model(self.initial_info)
        if self._send_buffer:
            await self._handle_info_update(DeviceInfoFromClientWS())

    async def _handle_message(self, message: str):
        info = DeviceInfo.model_validate_json(message)
        self._server_side_info = info
        self.on_server_side_info_updated.task_gather(self, info)

    async def _handle_info_update(self, info: DeviceInfoFromClientWS):
        if info.replace:
            self._send_buffer = info.model_dump(exclude_unset=True)
        else:
            self._send_buffer = deep_update(
                self._send_buffer,
                info.model_dump(exclude_unset=True),
            )
        if self.connected:
            await self._debounced_send_buf()


def get_ws_url() -> str:
    base = qconfig.get(config.serverUrl).replace("http", "ws", 1).rstrip("/")
    return f"{base}/api/v1/device/{qconfig.get(config.deviceKey)}/info"


info_feeder = DeviceInfoFeeder(
    get_ws_url(),
    qconfig.get(config.serverSecret),
    DeviceInfoFromClientWS.model_validate(get_initial_device_info_dict()),
    proxy=qconfig.get(config.serverConnectProxy) or True,
)


def on_config_enable_change(v: bool):
    if v:
        info_feeder.run_in_background()
    else:
        info_feeder.stop_background()


def on_config_url_change(_: str):
    info_feeder.endpoint = get_ws_url()


def on_config_secret_change(v: str):
    info_feeder.update_secret(v)


def on_config_proxy_change(v: str):
    info_feeder.proxy = v or True


def on_config_device_attr_change(
    attr: str,
    v: Any | None,
    falsy_default: Any = None,
):
    v_is_none = v is None
    if falsy_default and (not v):
        v = falsy_default
    setattr(info_feeder.initial_info, attr, v)
    if v_is_none:
        info_feeder.initial_info.model_fields_set.remove(attr)

    if not info_feeder.connected:
        # we have changed the initial info
        # and we will send the initial info before any message after connected
        # the initial info have set replace=True
        # so we don't need to care about updating now
        return

    if not v_is_none:
        info_feeder.update_info(DeviceInfoFromClientWS.model_validate({attr: v}))
        return

    # if original v is None, meaning using server side config
    # then we need to remove the attr from server side stored data
    # so we replace the entire info with target attr excluded
    info = info_feeder.server_side_info
    if info:
        info = DeviceInfoFromClientWS.model_validate(
            info.model_dump(exclude_unset=True),
        )
        setattr(info, attr, None)
        info.model_fields_set.remove(attr)
    else:
        info = info_feeder.initial_info
    info.replace = True
    info_feeder.update_info(info)


def on_config_key_change(_: Any):
    info_feeder.endpoint = get_ws_url()


def on_config_description_change(v: Any):
    on_config_device_attr_change("description", v or None)


def on_config_device_type_change(_: Any):
    on_config_device_attr_change("device_type", get_device_type())


def on_config_device_os_change(_: Any):
    on_config_device_attr_change("device_os", get_device_os())


def on_config_device_auto_remove_change(_: Any):
    on_config_device_attr_change(
        "remove_when_offline",
        (
            qconfig.get(config.deviceRemoveWhenOfflineOverrideValue)
            if qconfig.get(config.deviceRemoveWhenOfflineOverrideEnable)
            else None
        ),
        falsy_default=False,
    )


config.serverEnableConnect.valueChanged.connect(on_config_enable_change)
config.serverUrl.valueChanged.connect(on_config_url_change)
config.serverSecret.valueChanged.connect(on_config_secret_change)
config.serverConnectProxy.valueChanged.connect(on_config_proxy_change)

config.deviceKey.valueChanged.connect(on_config_key_change)
config.deviceDescription.valueChanged.connect(on_config_description_change)

config.deviceTypeOverrideUseDefault.valueChanged.connect(on_config_device_type_change)
config.deviceTypeOverrideEnable.valueChanged.connect(on_config_device_type_change)
config.deviceTypeOverrideUseCustom.valueChanged.connect(on_config_device_type_change)
config.deviceTypeOverrideValueBuiltIn.valueChanged.connect(on_config_device_type_change)
config.deviceTypeOverrideValueCustom.valueChanged.connect(on_config_device_type_change)

config.deviceOSOverrideUseDetect.valueChanged.connect(on_config_device_os_change)
config.deviceOSOverrideEnable.valueChanged.connect(on_config_device_os_change)
config.deviceOSOverrideValue.valueChanged.connect(on_config_device_os_change)

config.deviceRemoveWhenOfflineOverrideEnable.valueChanged.connect(
    on_config_device_auto_remove_change,
)
config.deviceRemoveWhenOfflineOverrideValue.valueChanged.connect(
    on_config_device_auto_remove_change,
)
