import ssl
from enum import StrEnum, auto
from ipaddress import IPv4Address
from pathlib import Path
from typing import ClassVar, override

from pydantic import BaseModel, ConfigDict, IPvAnyAddress
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class AppConfig(BaseModel):
    host: IPvAnyAddress = IPv4Address("127.0.0.1")
    port: int = 29306  # sle(e)py

    ws_max_size: int = 16777216
    ws_max_queue: int = 32
    ws_ping_interval: float | None = 20.0
    ws_ping_timeout: float | None = 20.0
    ws_per_message_deflate: bool = True
    reload: bool = False
    reload_dirs: list[str] | str | None = None
    reload_includes: list[str] | str | None = None
    reload_excludes: list[str] | str | None = None
    reload_delay: float = 0.25
    workers: int | None = None
    log_level: str | int | None = None
    access_log: bool = True
    proxy_headers: bool = True
    server_header: bool = True
    date_header: bool = True
    forwarded_allow_ips: list[str] | str | None = None
    root_path: str = ""
    limit_concurrency: int | None = None
    backlog: int = 2048
    limit_max_requests: int | None = None
    timeout_keep_alive: int = 5
    timeout_graceful_shutdown: int | None = None
    ssl_keyfile: Path | None = None
    ssl_certfile: Path | None = None
    ssl_keyfile_password: str | None = None
    ssl_version: int = ssl.PROTOCOL_TLS_SERVER
    ssl_cert_reqs: int = ssl.CERT_NONE
    ssl_ca_certs: str | None = None
    ssl_ciphers: str = "TLSv1"
    headers: list[tuple[str, str]] | None = None
    use_colors: bool | None = None
    app_dir: str | None = None
    factory: bool = False
    h11_max_incomplete_event_size: int | None = None


class CORSConfig(BaseModel):
    allow_origins: list[str] = ["*"]
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]
    allow_credentials: bool = True
    allow_origin_regex: str | None = None
    expose_headers: list[str] = []
    max_age: int = 600


class DeviceType(StrEnum):
    PC = auto()
    PHONE = auto()
    TABLET = auto()
    SMARTWATCH = auto()
    UNKNOWN = auto()


class DeviceOS(StrEnum):
    WINDOWS = auto()
    MACOS = auto()
    LINUX = auto()
    ANDROID = auto()
    IOS = auto()
    UNKNOWN = auto()


class OnlineStatus(StrEnum):
    ONLINE = auto()
    OFFLINE = auto()
    IDLE = auto()
    UNKNOWN = auto()


class DeviceConfig(BaseModel):
    name: str
    description: str | None = None
    device_type: DeviceType | str = DeviceType.UNKNOWN
    device_os: DeviceOS | str = DeviceOS.UNKNOWN


class FrontendStatusConfig(BaseModel):
    name: str
    description: str
    color: str


class FrontendConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    username: str = "LgCookie"

    status: dict[OnlineStatus, FrontendStatusConfig] = {
        OnlineStatus.ONLINE: FrontendStatusConfig(
            name="活着",
            description="目前在线，可以通过任意可用的联系方式联系到我。",
            color="var(--color-online)",
        ),
        OnlineStatus.OFFLINE: FrontendStatusConfig(
            name="似了",
            description="目前没有设备在线。",
            color="var(--color-offline)",
        ),
        OnlineStatus.IDLE: FrontendStatusConfig(
            name="空闲",
            description="所有设备都在空闲状态，可能正在休息。",
            color="var(--color-idle)",
        ),
        OnlineStatus.UNKNOWN: FrontendStatusConfig(
            name="未知",
            description="好像没有配置任何设备呢……",
            color="var(--color-unknown)",
        ),
    }


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_prefix="sleepy_",
        env_file_encoding="utf-8",
    )

    environment: ClassVar[str] = "prod"

    docs_url: str | None = None
    static_dir: Path | None = None

    secret: str | None = "sleepy"  # noqa: S105
    privacy_mode: bool = False

    poll_offline_timeout: int = 10
    frontend_event_throttle: float = 1
    allow_new_devices: bool = False

    app: AppConfig = AppConfig()
    cors: CORSConfig = CORSConfig()
    frontend: FrontendConfig = FrontendConfig()
    devices: dict[str, DeviceConfig] = {}

    @override
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        toml_settings = TomlConfigSettingsSource(settings_cls, "sleepy.toml")
        env_toml_settings = TomlConfigSettingsSource(
            settings_cls,
            f"sleepy.{cls.environment}.toml",
        )
        env_dotenv_settings = DotEnvSettingsSource(
            settings_cls,
            f".env.{cls.environment}",
        )
        return (
            init_settings,
            file_secret_settings,
            env_toml_settings,
            env_dotenv_settings,
            toml_settings,
            dotenv_settings,
            env_settings,
        )


class _EnvironmentConfig(BaseSettings):
    model_config = Config.model_config

    environment: str = "prod"

    @override
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        toml_settings = TomlConfigSettingsSource(settings_cls, "sleepy.toml")
        return (
            init_settings,
            file_secret_settings,
            toml_settings,
            dotenv_settings,
            env_settings,
        )


def _load_config():
    environment = _EnvironmentConfig().environment
    Config.environment = environment
    return Config()


config = _load_config()
