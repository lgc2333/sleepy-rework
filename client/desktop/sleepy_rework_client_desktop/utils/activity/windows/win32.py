from ctypes import windll

from .win32_types import (
    EVENT_OBJECT_NAMECHANGE,
    EVENT_SYSTEM_FOREGROUND,
    WINEVENT_OUTOFCONTEXT,
    WinEventProc,
)


def set_win_event_hook(
    event_min: int,
    event_max: int,
    hmod_win_event_proc: int | None,
    pfn_win_event_proc: WinEventProc,
    id_process: int,
    id_thread: int,
    dw_flags: int,
) -> int:
    """https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwineventhook"""
    return windll.user32.SetWinEventHook(
        event_min,
        event_max,
        hmod_win_event_proc or 0,
        pfn_win_event_proc.c_ptr,
        id_process,
        id_thread,
        dw_flags,
    )


def unhook_win_event(hwnd: int) -> bool:
    """https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-unhookwinevent"""
    return bool(windll.user32.UnhookWinEvent(hwnd))


def set_foreground_change_hook(callback: WinEventProc):
    return set_win_event_hook(
        EVENT_SYSTEM_FOREGROUND,
        EVENT_SYSTEM_FOREGROUND,
        0,
        callback,
        0,
        0,
        WINEVENT_OUTOFCONTEXT,
    )


def set_object_name_change_hook(
    callback: WinEventProc,
    tid: int = 0,
    pid: int = 0,
):
    return set_win_event_hook(
        EVENT_OBJECT_NAMECHANGE,
        EVENT_OBJECT_NAMECHANGE,
        0,
        callback,
        pid,
        tid,
        WINEVENT_OUTOFCONTEXT,
    )
