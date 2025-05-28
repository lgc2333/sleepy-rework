from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class ErrType(StrEnum):
    pass


class ErrDetail(BaseModel):
    type: ErrType | None = None
    msg: str | None = None
    data: Any = None
