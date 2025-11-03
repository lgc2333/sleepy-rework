from ctypes import WINFUNCTYPE
from ctypes.wintypes import DWORD, HWND, LONG
from typing import Protocol, final

EVENT_SYSTEM_FOREGROUND = 0x0003
EVENT_OBJECT_NAMECHANGE = 0x800C

WINEVENT_OUTOFCONTEXT = 0x0000


@final
class WinEventProc:
    CType = WINFUNCTYPE(
        None,
        DWORD,
        DWORD,
        HWND,
        LONG,
        LONG,
        DWORD,
        DWORD,
    )

    class Def(Protocol):
        def __call__(
            self,
            h_win_event_hook: int,
            event: int,
            hwnd: int,
            id_object: int,
            id_child: int,
            id_event_thread: int,
            dwms_event_time: int,
            /,
        ) -> None: ...

    def __init__(self, func: Def) -> None:
        self.func = func
        self.c_ptr = self.CType(func)
