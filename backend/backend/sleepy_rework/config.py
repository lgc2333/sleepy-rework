from typing import Any, ClassVar, override

from pydantic import model_validator
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from sleepy_rework_types import Config as BaseConfig, FrontendStatusConfig, OnlineStatus

DEFAULT_FRONTEND_STATUSES = {
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
        description="所有在线设备都在空闲状态，可能正在休息。",
        color="var(--color-idle)",
    ),
    OnlineStatus.UNKNOWN: FrontendStatusConfig(
        name="未知",
        description="好像没有配置任何设备呢……",
        color="var(--color-unknown)",
    ),
}


class Config(BaseConfig, BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_prefix="sleepy_",
        env_file_encoding="utf-8",
    )

    cls_environment: ClassVar[str | None] = None

    @model_validator(mode="before")
    @classmethod
    def _validate_override_frontend_statuses(cls, raw: Any):
        if not (
            isinstance(raw, dict)
            and isinstance((frontend := raw.get("frontend")), dict)
            and isinstance((status := frontend.get("status")), dict)
        ):
            # let pydantic validate the wrong type and raise validation error
            return raw

        merged: dict = DEFAULT_FRONTEND_STATUSES.copy()
        for k, v in status.items():
            if k not in DEFAULT_FRONTEND_STATUSES:
                continue
            if isinstance(v, dict):
                merged[k] = {**DEFAULT_FRONTEND_STATUSES[k].model_dump(), **v}
            else:
                merged[k] = v  # there also
        raw["frontend"]["status"] = merged

        return raw

    @model_validator(mode="after")
    def _correct_environment(self):
        if self.cls_environment:
            self.environment = self.cls_environment
        return self

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

        if not cls.cls_environment:
            return (
                init_settings,
                file_secret_settings,
                toml_settings,
                dotenv_settings,
                env_settings,
            )

        env = cls.cls_environment
        env_toml_settings = TomlConfigSettingsSource(settings_cls, f"sleepy.{env}.toml")
        env_dot_env_settings = DotEnvSettingsSource(settings_cls, f".env.{env}")
        return (
            init_settings,
            file_secret_settings,
            env_toml_settings,
            env_dot_env_settings,
            toml_settings,
            dotenv_settings,
            env_settings,
        )


def _load_config():
    environment = Config().environment
    Config.cls_environment = environment
    return Config()


config = _load_config()
