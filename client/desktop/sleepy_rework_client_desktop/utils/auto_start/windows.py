import os
import traceback
from pathlib import Path
from typing import override

from pylnk3 import Lnk, for_file

from ..common import get_start_args
from .base import BaseAutoStartManager

FILE_PATH = Path(
    r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\SleepyRework.lnk",
).expanduser()


class WindowsAutoStartManager(BaseAutoStartManager):
    @override
    @staticmethod
    def _is_enabled() -> bool:
        if not FILE_PATH.exists():
            return False
        args = get_start_args()
        try:
            lnk = Lnk(str(FILE_PATH))
        except Exception:
            traceback.print_exc()
            return False
        else:
            return (
                lnk.path == args[0]
                and lnk.arguments == " ".join(args[1:])
                and lnk.work_dir == os.getcwd()  # noqa: PTH109
            )

    @override
    @staticmethod
    def _enable() -> bool:
        args = get_start_args()
        try:
            for_file(
                args[0],
                str(FILE_PATH),
                arguments=" ".join(args[1:]),
                work_dir=os.getcwd(),  # noqa: PTH109
            )
        except Exception:
            traceback.print_exc()
            return False
        return True

    @override
    @staticmethod
    def _disable() -> bool:
        try:
            FILE_PATH.unlink(missing_ok=True)
        except Exception:
            traceback.print_exc()
            return False
        return True
