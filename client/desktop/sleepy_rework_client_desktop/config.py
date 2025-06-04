import sys
from typing import Any, cast, override

from nonestorage import user_config_dir
from pydantic import AnyUrl, UrlConstraints
from PyQt5.QtGui import QColor
from qfluentwidgets import (
    BoolValidator,
    ConfigItem,
    ConfigValidator,
    EnumSerializer,
    OptionsConfigItem,
    OptionsValidator,
    QConfig,
    Theme,
    qconfig,
    setTheme,
    setThemeColor,
)
from qframelesswindow.utils import getSystemAccentColor

from sleepy_rework_types import DeviceOS, DeviceType

configDir = user_config_dir("SleepyRework", roaming=True)
configFilePath = configDir / "config.json"
print(f"Config path: {configFilePath}")


class StringValidator(ConfigValidator):
    @override
    def validate(self, value: Any):  # pyright: ignore
        return isinstance(value, str)

    @override
    def correct(self, value: Any):
        return str(value)


class AnyProxyUrl(AnyUrl):
    _constraints = UrlConstraints(
        allowed_schemes=["http", "https", "socks5", "socks5h"],
    )


class ProxyURLValidator(ConfigValidator):
    @override
    def validate(self, value: Any):  # pyright: ignore
        if not isinstance(value, str):
            return False
        if value:
            try:
                AnyProxyUrl(value)
            except ValueError:
                return False
        return True

    @override
    def correct(self, value: Any):
        if self.validate(value):
            return value
        return ""


class Config(QConfig):
    serverEnableConnect = ConfigItem(
        "server",
        "enableConnect",
        default=False,
        validator=BoolValidator(),
    )
    serverUrl = ConfigItem(
        "server",
        "url",
        "127.0.0.1:29306",
        validator=StringValidator(),
    )
    serverSecret = ConfigItem(
        "server",
        "secret",
        "sleepy",
        validator=StringValidator(),
    )
    serverConnectProxy = ConfigItem(
        "server",
        "connectProxy",
        "",
        validator=ProxyURLValidator(),
    )

    appAutoStart = ConfigItem(
        "app",
        "autoStart",
        default=False,
        validator=BoolValidator(),
    )
    appStartMinimized = ConfigItem(
        "app",
        "startMinimized",
        default=False,
        validator=BoolValidator(),
    )
    appThemeMode = OptionsConfigItem(
        "app",
        "themeMode",
        Theme.AUTO,
        OptionsValidator(Theme),
        EnumSerializer(Theme),
    )

    deviceKey = ConfigItem(
        "device",
        "key",
        "",
        validator=StringValidator(),
    )
    deviceName = ConfigItem(
        "device",
        "name",
        "Desktop Device",
        validator=StringValidator(),
    )
    deviceDescription = ConfigItem(
        "device",
        "description",
        "",
        validator=StringValidator(),
    )

    deviceTypeOverrideUseDetect = ConfigItem(
        "device",
        "typeOverrideUseDetect",
        default=True,
        validator=BoolValidator(),
    )
    deviceTypeOverrideEnable = ConfigItem(
        "device",
        "typeOverrideEnable",
        default=False,
        validator=BoolValidator(),
    )
    deviceTypeOverrideUseCustom = ConfigItem(
        "device",
        "typeOverrideUseCustom",
        default=False,
        validator=BoolValidator(),
    )
    deviceTypeOverrideValueBuiltIn = OptionsConfigItem(
        "device",
        "typeOverrideValueBuiltIn",
        DeviceType.PC,
        validator=OptionsValidator(DeviceType),
    )
    deviceTypeOverrideValueCustom = ConfigItem(
        "device",
        "typeOverrideValueCustom",
        "unknown",
        validator=StringValidator(),
    )

    deviceOSOverrideUseDetect = ConfigItem(
        "device",
        "osOverrideUseDetect",
        default=True,
        validator=BoolValidator(),
    )
    deviceOSOverrideEnable = ConfigItem(
        "device",
        "osOverrideEnable",
        default=False,
        validator=BoolValidator(),
    )
    deviceOSOverrideUseCustom = ConfigItem(
        "device",
        "osOverrideUseCustom",
        default=False,
        validator=BoolValidator(),
    )
    deviceOSOverrideValueBuiltIn = OptionsConfigItem(
        "device",
        "osOverrideValueBuiltIn",
        DeviceOS.WINDOWS,
        validator=OptionsValidator(DeviceOS.UNKNOWN),
    )
    deviceOSOverrideValueCustom = ConfigItem(
        "device",
        "osOverrideValueCustom",
        "unknown",
        validator=StringValidator(),
    )


def reApplyThemeMode(theme: Theme | None = None):
    if theme is None:
        theme = cast("Theme", qconfig.get(config.appThemeMode))
    setTheme(theme, save=True, lazy=True)


def reApplyThemeColor():
    color = (
        getSystemAccentColor()
        if sys.platform in ["win32", "darwin"]
        else QColor("#f2a62a")
    )
    setThemeColor(color, save=True, lazy=True)


Config.appThemeMode.valueChanged.connect(reApplyThemeMode)

config = Config()
qconfig.load(configFilePath, config)

reApplyThemeMode()
reApplyThemeColor()

if not config.deviceKey.value:
    import random
    import string

    qconfig.set(
        config.deviceKey,
        "".join(random.sample(string.ascii_letters + string.digits, 8)),
    )
