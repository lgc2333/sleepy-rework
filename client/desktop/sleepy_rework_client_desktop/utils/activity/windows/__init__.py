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
from .win32 import (
    set_foreground_change_hook,
    set_object_name_change_hook,
    unhook_win_event,
)
from .win32_types import WinEventProc

CHECK_TASK_INTERVAL = 10  # s
IDLE_TIME = 300000  # ms, 300s
IGNORE_PROCESSES = {"explorer.exe"}


class WindowsActivityDetector(BasicActivityDetector):
    def __init__(self) -> None:
        super().__init__()
        self._win_task: Task | None = None

        self._last_tid: int = 0
        self._last_pid: int = 0
        self._last_app_change_time: float = 0

        self._curr_fg_hook_h: int = 0
        self._curr_name_hook_h: int = 0

        self._fg_hook_ptr = WinEventProc(self._foreground_change_hook_fn)
        self._name_hook_ptr = WinEventProc(self._name_change_hook_fn)

    def update_app_from_hwnd(self, hwnd: int, changed: bool = False):
        if changed:
            self._last_app_change_time = time.time() * 1000
        title = self.process_app_name(win32gui.GetWindowText(hwnd))
        app = DeviceCurrentApp(
            name=title,
            last_change_time=int(self._last_app_change_time),
        )
        self.update_current_app(app)

    def should_ignore(self, pid: int):
        try:
            p = psutil.Process(pid)
            return p.name() in IGNORE_PROCESSES
        except Exception:
            traceback.print_exc()
        return True

    def _name_change_hook_fn(
        self,
        _h_win_event_hook: int,
        _event: int,
        hwnd: int,
        id_object: int,
        _id_child: int,
        id_event_thread: int,
        _dwms_event_time: int,
    ):
        if id_object != 0 or id_event_thread != self._last_tid:
            return
        self.update_app_from_hwnd(hwnd)

    def _foreground_change_hook_fn(
        self,
        _h_win_event_hook: int,
        _event: int,
        hwnd: int,
        _id_object: int,
        _id_child: int,
        _id_event_thread: int,
        _dwms_event_time: int,
    ):
        tid, pid = win32process.GetWindowThreadProcessId(hwnd)
        if (tid == self._last_tid and pid == self._last_pid) or self.should_ignore(pid):
            return

        self._last_tid = tid
        self._last_pid = pid

        if self._curr_name_hook_h:
            unhook_win_event(self._curr_name_hook_h)

        self.update_app_from_hwnd(hwnd, changed=True)

        self._curr_name_hook_h = set_object_name_change_hook(
            self._name_hook_ptr,
            tid,
            pid,
        )

    async def _task_func_inner(self):
        # idle
        last_inp = win32api.GetLastInputInfo()
        curr = win32api.GetTickCount()
        idle = curr - last_inp >= IDLE_TIME
        self.update_idle(idle=idle)

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

        self.update_app_from_hwnd(win32gui.GetForegroundWindow(), changed=True)

        self._curr_fg_hook_h = set_foreground_change_hook(self._fg_hook_ptr)
        self._win_task = asyncio.create_task(self._task_func())

    @override
    def dispose(self):
        super().dispose()
        if self._curr_fg_hook_h:
            unhook_win_event(self._curr_fg_hook_h)
        if self._curr_name_hook_h:
            unhook_win_event(self._curr_name_hook_h)
