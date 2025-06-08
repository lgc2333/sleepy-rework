from abc import ABC, abstractmethod
from typing import Any

from sleepy_rework_types import DeviceCurrentApp

from ..common import SafeLoggedSignal


class BaseActivityDetector(ABC):
    def __init__(self) -> None:
        self._idle: bool = False
        self._current_app: DeviceCurrentApp | None = None

        self.on_idle_change = SafeLoggedSignal[[self, bool], None]()
        self.on_current_app_update = SafeLoggedSignal[
            [self, DeviceCurrentApp | None],
            Any,
        ]()

    @property
    def idle(self) -> bool:
        return self._idle

    @property
    def current_app(self) -> DeviceCurrentApp | None:
        return self._current_app

    def update_idle(self, idle: bool) -> None:
        if self._idle == idle:
            return
        self._idle = idle
        self.on_idle_change.task_gather(self, idle)

    def update_current_app(self, app: DeviceCurrentApp | None) -> None:
        self._current_app = app
        self.on_current_app_update.task_gather(self, app)

    @abstractmethod
    def setup(self) -> None: ...
