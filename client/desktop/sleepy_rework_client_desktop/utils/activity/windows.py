import asyncio
import time
import traceback
from asyncio import Task
from typing import override

import win32api
import win32gui

from sleepy_rework_types import DeviceCurrentApp

from .base import BaseActivityDetector

CHECK_INTERVAL = 1
IDLE_TIME = 300
MOUSE_IDLE_THRESHOLD = 5


class WindowsActivityDetector(BaseActivityDetector):
    def __init__(self) -> None:
        super().__init__()
        self._task: Task | None = None

        self._last_app_hwnd: int | None = None
        self._last_app_win_title: str | None = None
        self._last_app_change_time: float = 0

        self._last_mouse_move_time: float = 0
        self._last_mouse_pos: tuple[int, int] | None = None

    async def update_cursor_idle(self, curr_time: float):
        cur_pos = win32api.GetCursorPos()
        mouse_moved = (
            self._last_mouse_pos is None
            or abs(cur_pos[0] - self._last_mouse_pos[0]) >= MOUSE_IDLE_THRESHOLD
            or abs(cur_pos[1] - self._last_mouse_pos[1]) >= MOUSE_IDLE_THRESHOLD
        )
        if mouse_moved:
            self._last_mouse_move_time = curr_time
            self._last_mouse_pos = cur_pos
            self.update_idle(idle=False)
        elif curr_time - self._last_mouse_move_time >= IDLE_TIME:
            self.update_idle(idle=True)

    async def update_curr_window(self, curr_time: float):
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)

        if hwnd != self._last_app_hwnd:
            self._last_app_change_time = curr_time
            self._last_app_hwnd = hwnd
        elif title == self._last_app_win_title:
            # hwnd same, title same, skip update
            return
        self._last_app_win_title = title

        app = DeviceCurrentApp(
            name=title,
            last_change_time=int(self._last_app_change_time * 1000),
        )
        self.update_current_app(app)

    async def update_activity(self):
        curr_time = time.time()
        await self.update_cursor_idle(curr_time)
        await self.update_curr_window(curr_time)

    async def _task_func(self) -> None:
        while True:
            try:
                await self.update_activity()
            except Exception:
                traceback.print_exc()
            await asyncio.sleep(CHECK_INTERVAL)

    @override
    def setup(self) -> None:
        self._task = asyncio.create_task(self._task_func())
