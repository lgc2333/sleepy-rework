from typing import Annotated

from fastapi import Depends, Header, HTTPException, params, status

from sleepy_rework_types import ErrDetail

from ..config import config


async def auth_dep(
    x_sleepy_secret: Annotated[str | None, Header(alias="X-Sleepy-Secret")] = None,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> None:
    if (x_sleepy_secret == config.secret) or (
        authorization
        and authorization.startswith("Bearer ")
        and authorization[7:] == config.secret
    ):
        return
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, ErrDetail())


AuthDep: params.Depends = Depends(auth_dep)
Auth = Annotated[None, AuthDep]
