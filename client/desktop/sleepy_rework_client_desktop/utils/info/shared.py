import sys

from qfluentwidgets import qconfig

from sleepy_rework_types import DeviceType

from ...config import config


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
            return ""


def get_device_os() -> str | None:
    if qconfig.get(config.deviceOSOverrideUseDetect):
        return detect_device_os()
    if qconfig.get(config.deviceOSOverrideEnable):
        return qconfig.get(config.deviceOSOverrideValue)
    return None


def get_initial_device_info_dict():
    obj: dict = {"replace": True}
    if name := qconfig.get(config.deviceName):
        obj["name"] = name
    if description := qconfig.get(config.deviceDescription):
        obj["description"] = description
    if (device_type := get_device_type()) is not None:
        obj["device_type"] = device_type or None
    if (device_os := get_device_os()) is not None:
        obj["device_os"] = device_os or None
    if qconfig.get(config.deviceRemoveWhenOfflineOverrideEnable):
        obj["remove_when_offline"] = qconfig.get(
            config.deviceRemoveWhenOfflineOverrideValue,
        )
    return obj
