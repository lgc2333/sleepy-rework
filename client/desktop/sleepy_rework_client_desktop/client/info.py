from typing import Literal, Self

from debouncer import DebounceOptions, debounce

from sleepy_rework_types import DeviceInfoFromClient

from ..utils.common import SafeLoggedSignal
from .base import RetryWSClient

THROTTLE = 1


def make_debouncer():
    @debounce(
        THROTTLE,
        DebounceOptions(leading=True, trailing=True, time_window=THROTTLE),
    )
    async def f() -> Literal[True]:
        return True

    return f


class DeviceInfoFeeder(RetryWSClient[str]):
    def __init__(
        self,
        endpoint: str,
        initial_info: DeviceInfoFromClient,
        *,
        retry_sleep: int = 5,
    ):
        super().__init__(endpoint, retry_sleep=retry_sleep, decode=True)
        self.info = initial_info

        self.send_debouncer = make_debouncer()

        self.on_info_updated = SafeLoggedSignal[[Self, DeviceInfoFromClient], None]()
        # self.on_info_sent = SafeLoggedSignal[[Self, DeviceInfoFromClient], None]()

        self.on_connected.connect(lambda _: self.send_info())
        self.on_info_updated.connect(lambda _, __: self.send_info())

    def update_info(self, new_info: DeviceInfoFromClient | None = None):
        if new_info:
            self.info = new_info
        self.on_info_updated.task_gather(self, self.info)

    async def send_info(self):
        if (not self.send_debouncer()) or (not self.ws):
            return
        await self.ws.send(self.info.model_dump_json())
        # self.on_info_sent.task_gather(self, info)
