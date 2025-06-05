import sys
from typing import Any, cast, override

from nonestorage import user_config_dir
from pydantic import AnyHttpUrl, AnyUrl, UrlConstraints
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

from sleepy_rework_types import DeviceType

APP_NAME = "Sleepy Rework Desktop Client"
APP_ID = "sleepy_rework_client_desktop"
APP_PKG_NAME = "top.lgc2333.sleepy_rework.client_desktop"

configDir = user_config_dir(APP_NAME, roaming=True)
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


class URLValidator(ConfigValidator):
    def __init__(self, url: type[AnyUrl], default: str = "") -> None:
        super().__init__()
        self.url = url
        self.default = default

    @override
    def validate(self, value: Any):  # pyright: ignore
        if not isinstance(value, str):
            return False
        if value:
            try:
                self.url(value)
            except ValueError:
                return False
        return True

    @override
    def correct(self, value: Any):
        if self.validate(value):
            return value
        return self.default


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
        "http://127.0.0.1:29306",
        validator=URLValidator(AnyHttpUrl, "http://127.0.0.1:29306"),
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
        validator=URLValidator(AnyProxyUrl),
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

    deviceTypeOverrideUseDefault = ConfigItem(
        "device",
        "typeOverrideUseDefault",
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
        "",
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
    deviceOSOverrideValue = ConfigItem(
        "device",
        "osOverrideValue",
        "",
        validator=StringValidator(),
    )

    deviceRemoveWhenOfflineOverrideEnable = ConfigItem(
        "device",
        "removeWhenOfflineOverrideEnable",
        default=False,
        validator=BoolValidator(),
    )
    deviceRemoveWhenOfflineOverrideValue = ConfigItem(
        "device",
        "removeWhenOfflineOverrideValue",
        default=False,
        validator=BoolValidator(),
    )


config = Config()
qconfig.load(configFilePath, config)


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

reApplyThemeMode()
reApplyThemeColor()

if not qconfig.get(config.deviceKey):
    import random
    import string

    qconfig.set(
        config.deviceKey,
        "".join(random.sample(string.ascii_letters + string.digits, 8)),
    )
