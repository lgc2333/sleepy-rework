from typing import Annotated

from fastapi import Depends, HTTPException, WebSocket, params, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param

from sleepy_rework_types import ErrDetail

from ..config import config

bearer_auth = HTTPBearer(auto_error=False)
header_auth = APIKeyHeader(name="X-Sleepy-Secret", auto_error=False)


async def auth_dep(
    authorization: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_auth)],
    x_sleepy_secret: Annotated[str | None, Depends(header_auth)],
) -> None:
    if (x_sleepy_secret == config.secret) or (
        authorization and authorization.credentials == config.secret
    ):
        return
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, ErrDetail())


async def ws_auth_dep(ws: WebSocket):
    scheme, credentials = get_authorization_scheme_param(
        ws.headers.get("Authorization"),
    )
    if (scheme == "Bearer" and credentials == config.secret) or (
        ws.headers.get("X-Sleepy-Secret") == config.secret
    ):
        return
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, ErrDetail())


AuthDep: params.Depends = Depends(auth_dep)
WSAuthDep: params.Depends = Depends(ws_auth_dep)
