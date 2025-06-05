import json
from typing import Any, Self

from debouncer import DebounceOptions, debounce
from qfluentwidgets import qconfig

from sleepy_rework_types import DeviceInfo, DeviceInfoFromClientWS

from ..config import config
from ..utils.common import SafeLoggedSignal, deep_update
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
        kwargs.setdefault("additional_headers", {})
        kwargs["additional_headers"]["Authorization"] = f"Bearer {secret}"

        super().__init__(endpoint, decode=True, **kwargs)

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
    qconfig.get(config.serverUrl),
    qconfig.get(config.serverSecret),
    proxy=qconfig.get(config.serverConnectProxy),
)
