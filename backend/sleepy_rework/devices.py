import asyncio
import time
from asyncio import Future, TaskGroup, TimerHandle, get_running_loop
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any, Self

from fastapi import WebSocket, WebSocketDisconnect

from .config import DeviceConfig, OnlineStatus, config
from .log import logger
from .models import DeviceInfo, DeviceInfoRecv
from .utils import combine_model_from_model

type Co[T] = Coroutine[Any, Any, T]
type DeviceStatusUpdateHandler = Callable[[Device], Co[Any]]
type ManagerStatusUpdateHandler = Callable[["DeviceManager", Device], Co[Any]]


@dataclass
class Device:
    key: str
    info: DeviceInfo

    update_handlers: list[DeviceStatusUpdateHandler] = field(default_factory=list)

    _timer: TimerHandle | None = None
    _ws_connection: WebSocket | None = None

    @classmethod
    def new(cls, key: str, cfg: DeviceConfig, **kwargs) -> Self:
        return cls(
            key=key,
            info=DeviceInfo(**cfg.model_dump(exclude_unset=True)),
            **kwargs,
        )

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

    def offline_timer_handler(self):
        self.info.online = False
        asyncio.create_task(self.run_handlers())

    async def update(
        self,
        data: DeviceInfoRecv | None = None,
        online: bool = True,
        in_long_conn: bool = False,
    ):
        if self._timer is not None:
            self._timer.cancel()

        if in_long_conn or (not online):
            self._timer = None
        else:
            self._timer = get_running_loop().call_later(
                config.poll_offline_timeout,
                self.offline_timer_handler,
            )
            if self._ws_connection is not None:
                logger.warning(
                    f"Device '{self.info.name}' is connected using WebSocket,"
                    f" but received HTTP update data request."
                    f" Will disconnect WebSocket.",
                )
                try:
                    await self._ws_connection.close()
                except Exception:
                    logger.error("Error closing WebSocket connection")

        if data is not None:
            self.info = combine_model_from_model(self.info, data)
        self.info.online = online
        self.info.long_connection = in_long_conn
        self.info.last_update_time = int(time.time() * 1000)

        asyncio.create_task(self.run_handlers())

    async def handle_ws(self, ws: WebSocket):
        self._ws_connection = ws
        while True:
            try:
                data = DeviceInfoRecv.model_validate_json(await ws.receive_text())
                await self.update(data, in_long_conn=True)
            except WebSocketDisconnect:
                break
            except Exception:
                logger.exception("WebSocket error")
                break
        self._ws_connection = None
        if self._timer is None:
            await self.update(online=False)


class DeviceManager:
    def __init__(self, config: dict[str, DeviceConfig] | None = None) -> None:
        self.devices: dict[str, Device] = {}
        self.update_handlers: list[ManagerStatusUpdateHandler] = []

        if config:
            for key, cfg in config.items():
                self.add(key, cfg)

    @property
    def overall_status(self) -> OnlineStatus:
        if not self.devices:
            return (
                OnlineStatus.OFFLINE
                if config.unknown_as_offline
                else OnlineStatus.UNKNOWN
            )
        if any(x.info.online for x in self.devices.values()):
            if all(x.info.idle for x in self.devices.values() if x.info.online):
                return OnlineStatus.IDLE
            return OnlineStatus.ONLINE
        return OnlineStatus.OFFLINE

    def add(self, key: str, cfg: DeviceConfig) -> Device:
        device = Device.new(key, cfg, update_handlers=[self.update_handler])
        self.devices[key] = device
        return device

    def handle_update[F: ManagerStatusUpdateHandler](self, handler: F) -> F:
        self.update_handlers.append(handler)
        return handler

    async def update_handler(self, device: Device):
        if (not device.info.online) and device.info.remove_when_offline:
            del self.devices[device.key]

        async with TaskGroup() as tg:
            for handler in self.update_handlers:
                tg.create_task(handler(self, device))

    async def wait_update(self) -> Device:
        fut = Future()

        async def callback(_: "DeviceManager", device: Device):
            fut.set_result(device)
            self.update_handlers.remove(callback)

        self.handle_update(callback)
        return await fut


device_manager = DeviceManager(config.devices)
