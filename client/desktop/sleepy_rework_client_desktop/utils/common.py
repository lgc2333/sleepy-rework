import sys
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import Any

from cookit.common.signal import Signal
from qfluentwidgets import ConfigItem, qconfig

from sleepy_rework_types import DeviceType

from ..config import config

AUTO_START_OPT = "--auto-start"


def get_start_args(auto_start: bool = True) -> list[str]:
    args = []
    if getattr(sys, "frozen", False):
        args.append(sys.executable)
    else:
        assert __package__
        p_exec = Path(sys.executable)
        if "python" in p_exec.name:
            pw_exec = p_exec.with_name(p_exec.name.replace("python", "pythonw", 1))
            if pw_exec.exists():
                p_exec = pw_exec
        args.extend([str(p_exec), "-m", __package__.split(".")[0]])
    if auto_start:
        args.append(AUTO_START_OPT)
    return args


def get_override_config[M](
    use_detect: ConfigItem,
    enable: ConfigItem,
    use_custom: ConfigItem,
    value_builtin: ConfigItem,
    value_custom: ConfigItem,
    detector: Callable[[], Any],
    not_modified_val: Any = None,
) -> Any:
    if qconfig.get(use_detect):
        return detector()
    if not qconfig.get(enable):
        return not_modified_val
    if qconfig.get(use_custom):
        return qconfig.get(value_custom)
    return qconfig.get(value_builtin)


def get_device_type() -> str | None:
    if qconfig.get(config.deviceTypeOverrideUseDefault):
        return DeviceType.PC
    if not qconfig.get(config.deviceTypeOverrideEnable):
        return None
    if qconfig.get(config.deviceTypeOverrideUseCustom):
        return qconfig.get(config.deviceTypeOverrideValueCustom)
    return qconfig.get(config.deviceTypeOverrideValueBuiltIn)


def detect_device_os():
    match sys.platform:
        case "win32" | "cygwin":
            return "Windows"
        case "darwin":
            return "macOS"
        case "linux":
            return "Linux"
        case _:
            return "Unknown"


def get_device_os() -> str | None:
    if qconfig.get(config.deviceOSOverrideUseDetect):
        return detect_device_os()
    if qconfig.get(config.deviceOSOverrideEnable):
        return qconfig.get(config.deviceOSOverrideValue)
    return None


async def signal_exc_handler(_: Signal, e: Exception) -> Exception:
    traceback.print_exception(e)
    return e


class SafeLoggedSignal[**A, R](Signal[A, R, Exception]):
    def __init__(self) -> None:
        super().__init__(signal_exc_handler)
