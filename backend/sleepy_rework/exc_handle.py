from typing import TYPE_CHECKING, Any

from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import (
    HTTPException,
    RequestValidationError,
    WebSocketRequestValidationError,
)
from fastapi.utils import is_body_allowed_for_status_code
from fastapi.websockets import WebSocket
from starlette.requests import Request
from starlette.responses import Response

from sleepy_rework_types import ErrDetail
from sleepy_rework_types.models import WSErr


def transform_exc_detail(v: Any):
    if isinstance(v, ErrDetail):
        return v
    if isinstance(v, str):
        return ErrDetail(msg=v)
    return ErrDetail(data=jsonable_encoder(v))


def transform_exc_detail_json(v: Any) -> str:
    return transform_exc_detail(v).model_dump_json(exclude_unset=True)


async def close_ws_use_http_exc(ws: WebSocket, exc: HTTPException):
    we = WSErr(code=exc.status_code, detail=transform_exc_detail(exc.detail))
    await ws.close(
        code=status.WS_1008_POLICY_VIOLATION,
        reason=we.model_dump_json(exclude_unset=True),
    )


async def handle_http_exc(_request: Request, exc: Exception) -> Response:
    if TYPE_CHECKING:
        assert isinstance(exc, HTTPException)
    headers = getattr(exc, "headers", None)
    if not is_body_allowed_for_status_code(exc.status_code):
        return Response(status_code=exc.status_code, headers=headers)
    return Response(
        content=transform_exc_detail_json(exc.detail),
        status_code=exc.status_code,
        headers=headers,
        media_type="application/json",
    )


async def handle_validation_err(_request: Request, exc: Exception) -> Response:
    if TYPE_CHECKING:
        assert isinstance(exc, RequestValidationError)
    return Response(
        content=transform_exc_detail_json(exc.errors()),
        media_type="application/json",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def handle_ws_validation_err(websocket: WebSocket, exc: Exception) -> None:
    if TYPE_CHECKING:
        assert isinstance(exc, WebSocketRequestValidationError)
    await close_ws_use_http_exc(
        websocket,
        HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        ),
    )


def install_exc_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, handle_http_exc)
    app.add_exception_handler(RequestValidationError, handle_validation_err)
    app.add_exception_handler(WebSocketRequestValidationError, handle_ws_validation_err)
