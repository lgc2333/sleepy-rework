from typing import Annotated

from fastapi import Body, Depends, Form, Header, HTTPException, Query, params, status

from .config import config
from .log import logger
from .models import ErrDetail


async def auth_dep(
    body_secret: Annotated[str | None, Body(alias="secret")] = None,
    form_secret: Annotated[str | None, Form(alias="secret")] = None,
    query_secret: Annotated[str | None, Query(alias="secret")] = None,
    header_secret: Annotated[str | None, Header(alias="Sleepy-Secret")] = None,
    auth_header: Annotated[str | None, Header(alias="Authorization")] = None,
) -> None:
    if not config.secret:
        return

    literal_compares = (
        ("Body", body_secret),
        ("Form", form_secret),
        ("Query", query_secret),
        ("Header (Sleepy-Secret)", header_secret),
    )
    res = next((v for v in literal_compares if v[1] == config.secret), None)
    if res:
        logger.debug(f"[Auth] Verify secret Success from {res[0]}")
        return

    if (
        auth_header
        and auth_header.startswith("Bearer ")
        and auth_header[7:] == config.secret
    ):
        logger.debug("[Auth] Verify secret Success from Header (Authorization)")
        return

    logger.debug("[Auth] Verify secret Failed")
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, ErrDetail())


AuthDep: params.Depends = Depends(auth_dep)
Auth = Annotated[None, AuthDep]
