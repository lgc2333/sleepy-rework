import asyncio
import traceback
from asyncio import Task
from typing import Any, Self

import psutil
from psutil._common import sbattery
from qfluentwidgets import qconfig

from sleepy_rework_types import DeviceBatteryStatus, DeviceCurrentApp

from ...config import config
from ..common import SafeLoggedSignal, wrap_async

BATTERY_CHECK_INTERVAL = 3


def transform_battery_status(data: sbattery) -> DeviceBatteryStatus:
    return DeviceBatteryStatus(
        percent=data.percent,
        time_left=(
            data.secsleft
            # idk why it report 0xFFFFFFFF when power is unplugged recently
            if data.secsleft > 0 and data.secsleft < 0xFFFFFFFF
            else None
        ),
        charging=data.power_plugged,
    )


def detect_battery_status() -> DeviceBatteryStatus | None:
    try:
        data = psutil.sensors_battery()
    except Exception:
        traceback.print_exc()
    else:
        if data:
            return transform_battery_status(data)
    return None


class AdditionalStatusItem:
    def __init__(self, _content: str) -> None:
        self._content = _content
        self.on_content_update = SafeLoggedSignal[[Self, str], Any]()

    @property
    def content(self) -> str:
        return self._content

    def update_content(self, content: str) -> None:
        if self._content == content:
            return
        self._content = content
        self.on_content_update.task_gather(self, content)


class BasicActivityDetector:
    def __init__(self) -> None:
        self._idle: bool = False
        self._current_app: DeviceCurrentApp | None = None
        self._battery_status: DeviceBatteryStatus | None = None
        self._additional_statuses_items: list[AdditionalStatusItem] = []

        self._battery_task: Task | None = None

        self.on_idle_change = SafeLoggedSignal[[Self, bool], Any]()
        self.on_current_app_update = SafeLoggedSignal[
            [Self, DeviceCurrentApp | None],
            Any,
        ]()
        self.on_battery_status_update = SafeLoggedSignal[
            [Self, DeviceBatteryStatus | None],
            Any,
        ]()
        self.on_additional_statuses_update = SafeLoggedSignal[[Self, list[str]], Any]()

    @property
    def idle(self) -> bool:
        return self._idle

    @property
    def current_app(self) -> DeviceCurrentApp | None:
        return self._current_app

    @property
    def battery_status(self) -> DeviceBatteryStatus | None:
        return self._battery_status

    @property
    def additional_statuses(self) -> list[str]:
        return [status.content for status in self._additional_statuses_items]

    def process_app_name(self, name: str | None) -> str | None:
        if not name:
            return None

        name_parts = name.split(" - ")
        if qconfig.get(config.activityAppNameBrief):
            name = name_parts[-1]
        elif qconfig.get(config.activityAppNameReverse):
            name_parts.reverse()
            name = " - ".join(name_parts)

        if not name:
            return None

        filter_li: list[str] = qconfig.get(config.activityAppNameFilterList)
        is_blacked = any(
            True for x in filter_li if x and (x.casefold() in name.casefold())
        )
        if qconfig.get(config.activityAppNameFilterIsWhiteList):
            is_blacked = not is_blacked
        if is_blacked:
            name = None

        return name

    def update_idle(self, idle: bool) -> None:
        if self._idle == idle:
            return
        self._idle = idle
        self.on_idle_change.task_gather(self, idle)

    def update_current_app(self, app: DeviceCurrentApp | None) -> None:
        if self._current_app == app:
            return
        self._current_app = app
        self.on_current_app_update.task_gather(self, app)

    def update_battery_status(self, status: DeviceBatteryStatus | None) -> None:
        if self._battery_status == status:
            return
        self._battery_status = status
        self.on_battery_status_update.task_gather(self, status)

    def _on_additional_status_item_update(self):
        self.on_additional_statuses_update.task_gather(self, self.additional_statuses)

    def create_additional_status(self, content: str) -> AdditionalStatusItem:
        status = AdditionalStatusItem(content)
        self._additional_statuses_items.append(status)
        status.on_content_update.connect(
            lambda *_: wrap_async(self._on_additional_status_item_update),
        )
        self._on_additional_status_item_update()
        return status

    def remove_additional_status(self, status: AdditionalStatusItem) -> None:
        if status not in self._additional_statuses_items:
            return
        self._additional_statuses_items.remove(status)
        self._on_additional_status_item_update()

    async def _battery_task_func(self) -> None:
        while True:
            data = detect_battery_status()
            if not data:
                self._battery_task = None
                break
            self.update_battery_status(data)
            await asyncio.sleep(BATTERY_CHECK_INTERVAL)

    def setup(self) -> None:
        self._battery_task = asyncio.create_task(self._battery_task_func())
