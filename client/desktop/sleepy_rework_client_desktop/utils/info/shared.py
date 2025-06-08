import platform
from pathlib import Path

from qfluentwidgets import qconfig

from sleepy_rework_types import DeviceType

from ...config import config


def parse_env(env: str) -> dict[str, str | None]:
    env_lines = env.strip().splitlines()
    env_dict: dict[str, str | None] = {}

    for line in env_lines:
        if "=" not in line:
            env_dict[line.upper()] = None
            continue

        key, value = line.split("=", 1)
        env_dict[key.upper()] = value.strip("\"'").strip()

    return env_dict


def parse_env_file(env_file: str | Path) -> dict[str, str | None] | None:
    if not isinstance(env_file, Path):
        env_file = Path(env_file)
    if not env_file.exists():
        return None
    content = env_file.read_text(encoding="u8")
    return parse_env(content)


# Thanks to https://github.com/nonedesktop/nonebot-plugin-guestool/blob/main/nonebot_plugin_guestool/info.py
def get_linux_name_version() -> tuple[str, str] | None:
    env = parse_env_file("/etc/os-release")
    if env and (name := env.get("NAME")) and (version_id := env.get("VERSION_ID")):
        return name, version_id

    env = parse_env_file("/etc/lsb-release")
    if (
        env
        and (name := env.get("DISTRIB_ID"))
        and (version_id := env.get("DISTRIB_RELEASE"))
    ):
        return name, version_id

    return None


def detect_device_os():
    system, _, release, version, _, _ = platform.uname()
    system, release, version = platform.system_alias(system, release, version)

    if system == "Java":
        _, _, _, (system, release, _) = platform.java_ver()

    if system == "Darwin":
        return f"MacOS {platform.mac_ver()[0]}"

    if system == "Windows":
        return f"Windows {release}"

    if system == "Linux":
        if ver := get_linux_name_version():
            name, version_id = ver
            version = release if version_id.lower() == "rolling" else version_id
            return f"{name} {version}"

        return f"Linux {release}"

    return ""


def get_device_type() -> str | None:
    if qconfig.get(config.deviceTypeOverrideUseDefault):
        return DeviceType.PC
    if not qconfig.get(config.deviceTypeOverrideEnable):
        return None
    if qconfig.get(config.deviceTypeOverrideUseCustom):
        return qconfig.get(config.deviceTypeOverrideValueCustom)
    return qconfig.get(config.deviceTypeOverrideValueBuiltIn)


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
