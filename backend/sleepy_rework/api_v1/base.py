from typing import Annotated

from fastapi import APIRouter, Body, Response
from fastapi.exceptions import HTTPException

from ..config import FrontendConfig, config
from ..deps import AuthDep
from ..devices import device_manager
from ..models import DeviceDataOptional, Info, OpSuccess

router = APIRouter(prefix="/api/v1")


@router.get("")
async def _():
    return Response(content="💤", media_type="text/plain")


@router.get("/config/frontend")
async def _() -> FrontendConfig:
    return config.frontend


@router.get("/info")
async def _() -> Info:
    devices = (
        None
        if config.privacy_mode
        else {k: v.info for k, v in device_manager.devices.items()}
    )
    return Info(
        status=device_manager.status,
        devices=devices,
    )


@router.patch("/device/{device_key}/data", dependencies=[AuthDep])
async def _(device_key: str, data: Annotated[DeviceDataOptional, Body()]) -> OpSuccess:
    device = device_manager.devices.get(device_key)
    if not device:
        raise HTTPException(
            status_code=404,
            detail=f"Device '{device_key}' not found",
        )
    await device.update(data)
    return OpSuccess()
