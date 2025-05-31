from typing import Any, override

from nonestorage import user_config_dir
from qfluentwidgets import BoolValidator, ConfigItem, ConfigValidator, QConfig, qconfig

config_dir = user_config_dir("SleepyRework", roaming=True)
print(f"Config directory: {config_dir}")


class StringValidator(ConfigValidator):
    @override
    def validate(self, value: Any):  # pyright: ignore
        return isinstance(value, str)


class Config(QConfig):
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

    app_enable_send_status = ConfigItem(
        "app",
        "enable_send_status",
        default=False,
        validator=BoolValidator(),
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


config = Config()
qconfig.load(config_dir / "config.json", config)

if not config.device_key.value:
    import random
    import string

    qconfig.set(
        config.device_key,
        "".join(random.sample(string.ascii_letters + string.digits, 8)),
    )
