import asyncio
import time
from asyncio import Future, TaskGroup, TimerHandle, get_running_loop
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from .config import DeviceConfig, OnlineStatus, config
from .log import logger
from .models import DeviceData, DeviceInfo
from .utils import combine_model_from_model

type Co[T] = Coroutine[Any, Any, T]
type DeviceStatusUpdateHandler = Callable[[Device], Co[Any]]
type ManagerStatusUpdateHandler = Callable[["DeviceManager", Device], Co[Any]]


@dataclass
class Device:
    config: DeviceConfig
    info: DeviceInfo

    update_handlers: list[DeviceStatusUpdateHandler] = field(default_factory=list)

    _timer: TimerHandle | None = None
    _ws_connection: WebSocket | None = None

    @classmethod
    def from_config(cls, config: DeviceConfig, **kwargs) -> "Device":
        return cls(
            config=config,
            info=DeviceInfo(
                name=config.name,
                description=config.description,
            ),
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

    def set_offline(self):
        self.info.online = False
        asyncio.create_task(self.run_handlers())

    async def update(
        self,
        data: DeviceData | None = None,
        in_long_conn: bool = False,
    ):
        if self._timer is not None:
            self._timer.cancel()

        if in_long_conn:
            self._timer = None
        else:
            self._timer = get_running_loop().call_later(
                config.poll_offline_timeout,
                self.set_offline,
            )
            if self._ws_connection is not None:
                logger.warning(
                    f"Device '{self.config.name}' is connected using WebSocket,"
                    f" but received HTTP update data request."
                    f" Will disconnect WebSocket.",
                )
                try:
                    await self._ws_connection.close()
                except Exception:
                    logger.error("Error closing WebSocket connection")

        if data is not None:
            self.info.data = combine_model_from_model(
                self.info.data or DeviceData(),
                data,
            )
        self.info.online = True
        self.info.long_connection = in_long_conn
        self.info.last_update_time = int(time.time() * 1000)

        asyncio.create_task(self.run_handlers())

    async def handle_ws(self, ws: WebSocket):
        self._ws_connection = ws
        while True:
            try:
                data = DeviceData.model_validate_json(await ws.receive_text())
                await self.update(data, in_long_conn=True)
            except WebSocketDisconnect:
                break
            except Exception:
                logger.exception("WebSocket error")
                break
        self._ws_connection = None
        if self._timer is None:
            self.set_offline()


class DeviceManager:
    def __init__(self, config: dict[str, DeviceConfig]) -> None:
        self.devices = {
            name: Device.from_config(cfg, update_handlers=[self.update_handler])
            for name, cfg in config.items()
        }
        self.update_handlers: list[ManagerStatusUpdateHandler] = []

    @property
    def online_status(self) -> OnlineStatus:
        if not self.devices:
            return OnlineStatus.UNKNOWN
        if any(device.info.online for device in self.devices.values()):
            return OnlineStatus.ONLINE
        return OnlineStatus.OFFLINE

    def handle_update[F: ManagerStatusUpdateHandler](self, handler: F) -> F:
        self.update_handlers.append(handler)
        return handler

    async def update_handler(self, device: Device):
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
