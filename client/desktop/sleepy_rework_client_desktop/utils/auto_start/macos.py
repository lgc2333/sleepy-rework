from pathlib import Path
from typing import override
from xml.sax.saxutils import escape

from ...consts import APP_PKG_NAME
from ..common import get_start_args
from .base import BaseAutoStartManager

FILE_PATH = Path(f"~/Library/LaunchAgents/{APP_PKG_NAME}.plist").expanduser()

ARGS = "\n        ".join(f"<string>{escape(arg)}</string>" for arg in get_start_args())
FILE_CONTENT = f"""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{APP_PKG_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        {ARGS}
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""


class MacOSAutoStartManager(BaseAutoStartManager):
    @override
    @staticmethod
    def _is_enabled() -> bool:
        return FILE_PATH.exists() and FILE_PATH.read_text("u8") == FILE_CONTENT

    @override
    @staticmethod
    def _enable() -> bool:
        FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        FILE_PATH.touch(0o644)
        FILE_PATH.write_text(FILE_CONTENT, "u8")
        return True

    @override
    @staticmethod
    def _disable() -> bool:
        FILE_PATH.unlink(missing_ok=True)
        return True
