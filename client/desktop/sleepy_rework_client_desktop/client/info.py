import json
from typing import Any, Self

from debouncer import DebounceOptions, debounce
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
            self.on_before_send_info.task_gather(self, self._send_buffer)
            msg = json.dumps(self._send_buffer)
            self._send_buffer.clear()
            await self.ws.send(msg)

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

    async def _handle_connected(self):
        self._send_buffer.clear()
        await self._handle_info_update(self.initial_info)

    async def _handle_message(self, message: str):
        info = DeviceInfo.model_validate_json(message)
        self._server_side_info = info
        self.on_server_side_info_updated.task_gather(self, info)

    async def _handle_info_update(self, info: DeviceInfoFromClientWS):
        cache_is_replace = self._send_buffer.get("replace", False)
        info_is_place = info.replace
        should_send_now = cache_is_replace != info_is_place
        if should_send_now:
            self._send_buffer.clear()
            self._debounced_send_buf.cancel()
            buf = info.model_dump(exclude_unset=True)
            self.on_before_send_info.task_gather(self, buf)
            await self.ws.send(buf)
        else:
            deep_update(self._send_buffer, info.model_dump(exclude_unset=True))
            await self._debounced_send_buf()


info_feeder = DeviceInfoFeeder(
    qconfig.get(config.serverUrl).replace("http", "ws", 1),
    qconfig.get(config.serverSecret),
    DeviceInfoFromClientWS.model_validate(get_initial_device_info_dict()),
    proxy=qconfig.get(config.serverConnectProxy) or True,
)


def on_config_enable_change(v: bool):
    if v:
        info_feeder.run_in_background()
    else:
        info_feeder.stop_background()


def on_config_url_change(v: str):
    info_feeder.endpoint = v.replace("http", "ws", 1)


def on_config_secret_change(v: str):
    info_feeder.update_secret(v)


def on_config_proxy_change(v: str):
    info_feeder.proxy = v or True


def on_config_device_attr_change(attr: str, v: Any | None):
    # if v is None, meaning using server side config
    # then we need to remove the attr from server side stored data
    # so we replace the entire info with target attr excluded

    v_is_none = v is None
    v = v or None
    setattr(info_feeder.initial_info, attr, v)

    if not v_is_none:
        info_feeder.update_info(DeviceInfoFromClientWS.model_validate({attr: v}))
        return

    info_feeder.initial_info.model_fields_set.remove(attr)

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
    )


config.serverEnableConnect.valueChanged.connect(on_config_enable_change)
config.serverUrl.valueChanged.connect(on_config_url_change)
config.serverSecret.valueChanged.connect(on_config_secret_change)
config.serverConnectProxy.valueChanged.connect(on_config_proxy_change)

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
