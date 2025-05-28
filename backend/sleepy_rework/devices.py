import asyncio
import time
from asyncio import Future, TaskGroup, TimerHandle, get_running_loop
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any

from .config import DeviceConfig, config
from .log import logger
from .models import DeviceData, DeviceDataOptional, DeviceInfo, OnlineStatus, Status
from .utils import update_model_from_model

type Co[T] = Coroutine[Any, Any, T]
type DeviceStatusUpdateHandler = Callable[[Device], Co[Any]]
type ManagerStatusUpdateHandler = Callable[["DeviceManager", Device], Co[Any]]


@dataclass
class Device:
    config: DeviceConfig
    info: DeviceInfo

    update_handlers: list[DeviceStatusUpdateHandler] = field(default_factory=list)

    _timer: TimerHandle | None = None

    @classmethod
    def from_config(cls, config: DeviceConfig, **kwargs) -> "Device":
        return cls(config=config, info=DeviceInfo(name=config.name), **kwargs)

    def handle_update[F: DeviceStatusUpdateHandler](self, handler: F) -> F:
        self.update_handlers.append(handler)
        return handler

    async def run_handlers(self):
        try:
            async with TaskGroup() as tg:
                for handler in self.update_handlers:
                    tg.create_task(handler(self))
        except Exception:
            logger.exception("Error occurred while running device update handlers")

    def set_offline(self):
        self.info.online = False
        asyncio.create_task(self.run_handlers())

    async def update(self, data: DeviceDataOptional | None = None):
        if self._timer is not None:
            self._timer.cancel()
        self._timer = get_running_loop().call_later(
            config.heartbeat_timeout,
            self.set_offline,
        )

        if data is not None:
            self.info.data = update_model_from_model(
                self.info.data or DeviceData(),
                data,
            )
        self.info.online = True
        self.info.last_heartbeat_time = int(time.time() * 1000)

        asyncio.create_task(self.run_handlers())


class DeviceManager:
    def __init__(self, config: dict[str, DeviceConfig]) -> None:
        self.devices = {
            name: Device.from_config(cfg, update_handlers=[self.update_handler])
            for name, cfg in config.items()
        }
        self.update_handlers: list[ManagerStatusUpdateHandler] = []
        self._waiting_futures: list[Future[Device]] = []

    @property
    def online_status(self) -> OnlineStatus:
        if not self.devices:
            return OnlineStatus.UNKNOWN
        if all(device.info.online for device in self.devices.values()):
            return OnlineStatus.ONLINE
        return OnlineStatus.OFFLINE

    @property
    def status(self) -> Status:
        return Status(
            type=self.online_status,
            detail=config.frontend.status[self.online_status],
        )

    def handle_update[F: ManagerStatusUpdateHandler](self, handler: F) -> F:
        self.update_handlers.append(handler)
        return handler

    async def update_handler(self, device: Device):
        futures = self._waiting_futures.copy()
        self._waiting_futures.clear()
        for fut in futures:
            fut.set_result(device)

        async with TaskGroup() as tg:
            for handler in self.update_handlers:
                tg.create_task(handler(self, device))

    async def wait_update(self) -> Device:
        fut = Future()
        self._waiting_futures.append(fut)
        return await fut


device_manager = DeviceManager(config.devices)
