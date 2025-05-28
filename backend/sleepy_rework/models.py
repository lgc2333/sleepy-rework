from enum import StrEnum, auto
from typing import Any

from pydantic import BaseModel


class ErrType(StrEnum):
    NOT_AUTHORIZED = auto()


class ErrDetail(BaseModel):
    err: ErrType | None = None
    msg: str | None = None
    data: Any = None
