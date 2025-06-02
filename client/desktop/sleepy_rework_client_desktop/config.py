import sys
from typing import Any, override

from nonestorage import user_config_dir
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


class Config(QConfig):
    serverEnableSendStatus = ConfigItem(
        "server",
        "enableSendStatus",
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

    deviceEnableTypeDetect = ConfigItem(
        "device",
        "enableTypeDetect",
        default=True,
        validator=BoolValidator(),
    )
    deviceEnableTypeOverride = ConfigItem(
        "device",
        "enableTypeOverride",
        default=False,
        validator=BoolValidator(),
    )
    deviceIsCustomTypeOverride = ConfigItem(
        "device",
        "isCustomTypeOverride",
        default=False,
        validator=BoolValidator(),
    )
    deviceBuiltInTypeOverride = OptionsConfigItem(
        "device",
        "builtInTypeOverride",
        DeviceType.PC,
        validator=OptionsValidator(DeviceType),
    )
    deviceCustomTypeOverride = ConfigItem(
        "device",
        "customTypeOverride",
        "unknown",
        validator=StringValidator(),
    )

    deviceEnableOSDetect = ConfigItem(
        "device",
        "enableOSDetect",
        default=True,
        validator=BoolValidator(),
    )
    deviceEnableOSOverride = ConfigItem(
        "device",
        "enableOSOverride",
        default=False,
        validator=BoolValidator(),
    )
    deviceIsCustomOSOverride = ConfigItem(
        "device",
        "isCustomOSOverride",
        default=False,
        validator=BoolValidator(),
    )
    deviceBuiltInOSOverride = OptionsConfigItem(
        "device",
        "builtInOSOverride",
        DeviceOS.UNKNOWN,
        validator=OptionsValidator(DeviceOS.UNKNOWN),
    )
    deviceCustomOSOverride = ConfigItem(
        "device",
        "customOSOverride",
        "unknown",
        validator=StringValidator(),
    )


def _themeConfigChanged(theme: Theme):
    qconfig.set(qconfig.themeMode, theme)
    setTheme(theme)


Config.appThemeMode.valueChanged.connect(_themeConfigChanged)


config = Config()
qconfig.load(configFilePath, config)

_themeConfigChanged(qconfig.get(config.appThemeMode))
qconfig.set(
    config.themeColor,
    (
        getSystemAccentColor()
        if sys.platform in ["win32", "darwin"]
        else QColor("#f2a62a")
    ),
    save=False,
)

if not config.deviceKey.value:
    import random
    import string

    qconfig.set(
        config.deviceKey,
        "".join(random.sample(string.ascii_letters + string.digits, 8)),
    )
