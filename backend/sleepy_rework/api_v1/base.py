from debouncer import DebounceOptions, debounce
from fastapi import APIRouter, Response, WebSocket, WebSocketDisconnect
from fastapi.exceptions import HTTPException

from ..config import FrontendConfig, config
from ..devices import device_manager
from ..log import logger
from ..models import DeviceData, Info, OpSuccess
from .deps import AuthDep

router = APIRouter(prefix="/api/v1")


@router.get("")
async def _():
    return Response(content="💤", media_type="text/plain")


@router.get("/config/frontend")
async def _() -> FrontendConfig:
    return config.frontend


async def get_info() -> Info:
    devices = (
        None
        if config.privacy_mode
        else {k: v.info for k, v in device_manager.devices.items()}
    )
    return Info(status=device_manager.online_status, devices=devices)


@router.get("/info")
async def _() -> Info:
    return await get_info()


@router.websocket("/info")
async def _(ws: WebSocket):
    await ws.accept()

    @device_manager.handle_update
    @debounce(
        config.frontend_event_throttle,
        DebounceOptions(
            leading=True,
            trailing=True,
            time_window=config.frontend_event_throttle,
        ),
    )
    async def _handler(*_):
        await ws.send_text((await get_info()).model_dump_json())

    try:
        await _handler()
        while True:
            await ws.receive_bytes()
    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("WebSocket error")
    finally:
        device_manager.update_handlers.remove(_handler)


def find_device_http(device_key: str):
    device = device_manager.devices.get(device_key)
    if not device:
        raise HTTPException(
            status_code=404,
            detail=f"Device '{device_key}' not found",
        )
    return device


@router.patch("/device/{device_key}/data", dependencies=[AuthDep])
async def _(device_key: str, data: DeviceData | None = None) -> OpSuccess:
    device = find_device_http(device_key)
    await device.update(data)
    return OpSuccess()


@router.websocket("/device/{device_key}/data", dependencies=[AuthDep])
async def _(ws: WebSocket, device_key: str):
    device = find_device_http(device_key)
    await ws.accept()
    await device.handle_ws(ws)
