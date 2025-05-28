from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, WebSocketRequestValidationError
from fastapi.utils import is_body_allowed_for_status_code
from fastapi.websockets import WebSocket
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, WS_1008_POLICY_VIOLATION

from .models import ErrDetail


def transform_exc_detail(v: Any):
    if isinstance(v, ErrDetail):
        return v.model_dump_json()
    if isinstance(v, str):
        return ErrDetail(msg=v).model_dump_json()
    return ErrDetail(data=jsonable_encoder(v)).model_dump_json()


async def http_exception_handler(_request: Request, exc: HTTPException) -> Response:
    headers = getattr(exc, "headers", None)
    if not is_body_allowed_for_status_code(exc.status_code):
        return Response(status_code=exc.status_code, headers=headers)
    return Response(
        content=transform_exc_detail(exc.detail),
        status_code=exc.status_code,
        headers=headers,
        media_type="application/json",
    )


async def request_validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> Response:
    return Response(
        content=transform_exc_detail(exc.errors()),
        media_type="application/json",
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def websocket_request_validation_exception_handler(
    websocket: WebSocket,
    exc: WebSocketRequestValidationError,
) -> None:
    await websocket.close(
        code=WS_1008_POLICY_VIOLATION,
        reason=transform_exc_detail(exc.errors()),
    )


def install_exc_handlers(app: Any) -> None:
    app.add_exception_handler(
        HTTPException,
        http_exception_handler,
    )
    app.add_exception_handler(
        RequestValidationError,
        request_validation_exception_handler,
    )
    app.add_exception_handler(
        WebSocketRequestValidationError,
        websocket_request_validation_exception_handler,
    )
