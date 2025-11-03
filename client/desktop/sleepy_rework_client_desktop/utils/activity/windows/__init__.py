import asyncio
import time
import traceback
from asyncio import Task
from typing import override

import psutil
import win32api
import win32gui
import win32process

from sleepy_rework_types import DeviceCurrentApp

from ..basic import BasicActivityDetector

CHECK_TASK_INTERVAL = 1  # s
IDLE_TIME = 300000  # ms, 300s


class WindowsActivityDetector(BasicActivityDetector):
    def __init__(self) -> None:
        super().__init__()
        self._win_task: Task | None = None

        self._last_pid: int = 0
        self._last_title: str = ""
        self._last_app_change_time: int = 0  # ms

    # more stable than hooks... so rolled back. why?
    async def update_curr_window_task(self, curr_time: float):
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        if (not title) and psutil.Process(pid).name() == "explorer.exe":
            # ignore empty title of explorer windows
            return

        if title != self._last_title:
            self._last_title = title or ""
        if pid != self._last_pid:
            self._last_pid = pid
            self._last_app_change_time = int(curr_time * 1000)

        app = DeviceCurrentApp(
            name=self._last_title,
            last_change_time=self._last_app_change_time,
        )
        self.update_current_app(app)

    async def update_idle_task(self):
        last_inp = win32api.GetLastInputInfo()
        curr = win32api.GetTickCount()
        idle = curr - last_inp >= IDLE_TIME
        self.update_idle(idle=idle)

    async def _task_func_inner(self):
        curr_t = time.time()
        await self.update_curr_window_task(curr_t)
        await self.update_idle_task()

    async def _task_func(self) -> None:
        while True:
            try:
                await self._task_func_inner()
            except Exception:
                traceback.print_exc()
            await asyncio.sleep(CHECK_TASK_INTERVAL)

    @override
    def setup(self) -> None:
        super().setup()
        self._win_task = asyncio.create_task(self._task_func())

    @override
    def dispose(self):
        super().dispose()
        if self._win_task:
            self._win_task.cancel()
            self._win_task = None
