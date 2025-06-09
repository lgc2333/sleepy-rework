from pathlib import Path
from shlex import quote
from typing import override

from ...consts import APP_ID, APP_NAME
from ..common import get_start_args
from .base import BaseAutoStartManager

FILE_PATH = Path(
    f"~/.config/autostart/{APP_ID}.desktop",
).expanduser()

ARGS = " ".join(f"{quote(arg)}" for arg in get_start_args())
FILE_CONTENT = f"""\
[Desktop Entry]
Type=Application
Name={APP_NAME}
Exec={ARGS}
X-GNOME-Autostart-enabled=true
"""


class LinuxAutoStartManager(BaseAutoStartManager):
    @override
    @staticmethod
    def _is_enabled() -> bool:
        return FILE_PATH.exists() and FILE_PATH.read_text("u8") == FILE_CONTENT

    @override
    @staticmethod
    def _enable() -> bool:
        FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        FILE_PATH.touch(0o755)
        FILE_PATH.write_text(FILE_CONTENT, "u8")
        return True

    @override
    @staticmethod
    def _disable() -> bool:
        FILE_PATH.unlink(missing_ok=True)
        return True
