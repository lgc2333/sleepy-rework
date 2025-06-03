import ssl
from ipaddress import IPv4Address
from pathlib import Path

from pydantic import BaseModel, ConfigDict, IPvAnyAddress, field_validator

from .enums import DeviceOS, DeviceType, OnlineStatus


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
    forwarded_allow_ips: list[str] | str | None = "*"
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


class DeviceConfig(BaseModel):
    name: str | None = None
    description: str | None = None
    device_type: DeviceType | str = DeviceType.UNKNOWN
    device_os: DeviceOS | str = DeviceOS.UNKNOWN
    remove_when_offline: bool = False


class FrontendStatusConfig(BaseModel):
    name: str
    description: str
    color: str


class FrontendStatusConfigOptional(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None


class FrontendConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    username: str = "LgCookie"
    statuses: dict[OnlineStatus, FrontendStatusConfig] = {}

    @field_validator("statuses", mode="after")
    @classmethod
    def _validate_status(cls, v: dict):
        statuses = OnlineStatus.__members__.values()
        if any((x not in statuses) for x in v):
            raise ValueError("Invalid status keys in frontend configuration")
        return v


class Config(BaseModel):
    environment: str = "prod"
    docs_url: str | None = None
    static_dir: Path | None = None

    secret: str | None = "sleepy"  # noqa: S105
    privacy_mode: bool = False
    unknown_as_offline: bool = False

    poll_offline_timeout: int = 30
    frontend_event_throttle: float = 1
    allow_new_devices: bool = False

    app: AppConfig = AppConfig()
    cors: CORSConfig = CORSConfig()
    frontend: FrontendConfig = FrontendConfig()
    devices: dict[str, DeviceConfig] = {}
