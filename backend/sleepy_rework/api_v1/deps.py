from typing import Annotated

from fastapi import Depends, HTTPException, params, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

from sleepy_rework_types import ErrDetail

from ..config import config

bearer_auth = HTTPBearer(auto_error=False)
header_auth = APIKeyHeader(name="X-Sleepy-Secret", auto_error=False)


async def auth_dep(
    x_sleepy_secret: Annotated[str | None, Depends(header_auth)] = None,
    authorization: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_auth),
    ] = None,
) -> None:
    if (x_sleepy_secret == config.secret) or (
        authorization and authorization.credentials == config.secret
    ):
        return
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, ErrDetail())


AuthDep: params.Depends = Depends(auth_dep)
