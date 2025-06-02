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

config_dir = user_config_dir("SleepyRework", roaming=True)
config_file_path = config_dir / "config.json"
print(f"Config path: {config_file_path}")


class StringValidator(ConfigValidator):
    @override
    def validate(self, value: Any):  # pyright: ignore
        return isinstance(value, str)


class Config(QConfig):
    server_enable_send_status = ConfigItem(
        "server",
        "enable_send_status",
        default=False,
        validator=BoolValidator(),
    )
    server_url = ConfigItem(
        "server",
        "url",
        "127.0.0.1:29306",
        validator=StringValidator(),
    )
    server_secret = ConfigItem(
        "server",
        "secret",
        "sleepy",
        validator=StringValidator(),
    )

    app_auto_start = ConfigItem(
        "app",
        "auto_start",
        default=False,
        validator=BoolValidator(),
    )
    app_start_minimized = ConfigItem(
        "app",
        "start_minimized",
        default=False,
        validator=BoolValidator(),
    )
    app_theme_mode = OptionsConfigItem(
        "app",
        "theme_mode",
        Theme.AUTO,
        OptionsValidator(Theme),
        EnumSerializer(Theme),
    )

    device_key = ConfigItem(
        "device",
        "key",
        "",
        validator=StringValidator(),
    )
    device_name = ConfigItem(
        "device",
        "name",
        "Desktop Device",
        validator=StringValidator(),
    )
    device_description = ConfigItem(
        "device",
        "description",
        "",
        validator=StringValidator(),
    )


def _theme_config_changed(theme: Theme):
    qconfig.set(qconfig.themeMode, theme)
    setTheme(theme)


Config.app_theme_mode.valueChanged.connect(_theme_config_changed)


config = Config()
qconfig.load(config_file_path, config)

_theme_config_changed(qconfig.get(config.app_theme_mode))
qconfig.set(
    config.themeColor,
    (
        getSystemAccentColor()
        if sys.platform in ["win32", "darwin"]
        else QColor("#f2a62a")
    ),
    save=False,
)

if not config.device_key.value:
    import random
    import string

    qconfig.set(
        config.device_key,
        "".join(random.sample(string.ascii_letters + string.digits, 8)),
    )
