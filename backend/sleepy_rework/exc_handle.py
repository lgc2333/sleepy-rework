from typing import TYPE_CHECKING, Any

from fastapi import FastAPI
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
        return v.model_dump_json(exclude_unset=True)
    if isinstance(v, str):
        return ErrDetail(msg=v).model_dump_json(exclude_unset=True)
    return ErrDetail(data=jsonable_encoder(v)).model_dump_json(exclude_unset=True)


async def handle_http_exc(_request: Request, exc: Exception) -> Response:
    if TYPE_CHECKING:
        assert isinstance(exc, HTTPException)
    headers = getattr(exc, "headers", None)
    if not is_body_allowed_for_status_code(exc.status_code):
        return Response(status_code=exc.status_code, headers=headers)
    return Response(
        content=transform_exc_detail(exc.detail),
        status_code=exc.status_code,
        headers=headers,
        media_type="application/json",
    )


async def handle_validation_err(_request: Request, exc: Exception) -> Response:
    if TYPE_CHECKING:
        assert isinstance(exc, RequestValidationError)
    return Response(
        content=transform_exc_detail(exc.errors()),
        media_type="application/json",
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def handle_ws_validation_err(websocket: WebSocket, exc: Exception) -> None:
    if TYPE_CHECKING:
        assert isinstance(exc, WebSocketRequestValidationError)
    await websocket.close(
        code=WS_1008_POLICY_VIOLATION,
        reason=transform_exc_detail(exc.errors()),
    )


def install_exc_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, handle_http_exc)
    app.add_exception_handler(RequestValidationError, handle_validation_err)
    app.add_exception_handler(WebSocketRequestValidationError, handle_ws_validation_err)
