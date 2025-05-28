import os
import ssl
from ipaddress import IPv4Address

from pydantic import BaseModel, IPvAnyAddress
from pydantic_settings import BaseSettings, SettingsConfigDict

from .utils import deep_update


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
    ssl_keyfile: str | os.PathLike[str] | None = None
    ssl_certfile: str | os.PathLike[str] | None = None
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


class Config(BaseModel):
    environment: str = "prod"
    app: AppConfig = AppConfig()
    cors: CORSConfig = CORSConfig()


def _get_model_config(env: str | None = None):
    return SettingsConfigDict(
        env_prefix="sleepy_",
        env_file=f".env.{env}" if env else ".env",
        env_file_encoding="utf-8",
        toml_file=f"sleepy.{env}.toml" if env else "sleepy.toml",
    )


def _load_config():
    class SettingsConfig(Config, BaseSettings):
        model_config = _get_model_config()

    base_config = SettingsConfig()

    class FromEnvSettingsConfig(SettingsConfig):
        model_config = _get_model_config(base_config.environment)

    config_dict = deep_update(
        base_config.model_dump(exclude_unset=True),
        FromEnvSettingsConfig().model_dump(exclude_unset=True),
    )
    return Config.model_validate(config_dict)


config = _load_config()
