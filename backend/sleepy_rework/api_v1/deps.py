from typing import Annotated

from fastapi import Depends, Header, HTTPException, params, status

from ..config import config
from ..log import logger
from ..models import ErrDetail


async def auth_dep(
    x_sleepy_secret: Annotated[str | None, Header("X-Sleepy-Secret")] = None,
    authorization: Annotated[str | None, Header("Authorization")] = None,
) -> None:
    if (x_sleepy_secret == config.secret) or (
        authorization
        and authorization.startswith("Bearer ")
        and authorization[7:] == config.secret
    ):
        return

    logger.debug("[Auth] Verify secret Failed")
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, ErrDetail())


AuthDep: params.Depends = Depends(auth_dep)
Auth = Annotated[None, AuthDep]
