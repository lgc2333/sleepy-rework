import asyncio
from typing import Annotated

from debouncer import DebounceOptions, debounce
from fastapi import (
    APIRouter,
    Query,
    Response,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.exceptions import HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import ValidationError

from sleepy_rework_types import (
    DeviceConfig,
    DeviceInfo,
    DeviceInfoFromClient,
    DeviceInfoFromClientWS,
    ErrDetail,
    FrontendConfig,
    Info,
    OpSuccess,
    WSErr,
)

from ..config import config
from ..devices import Device, device_manager
from ..exc_handle import transform_exc_detail
from ..log import logger
from .deps import AuthDep

DESCRIPTION = """
## API v1 基础知识

### 类型定义

请参考 [sleepy_rework_types](https://github.com/lgc2333/sleepy-rework/blob/main/backend/types/sleepy_rework_types)

### 请求错误

所有请求在错误时均返回非 200 状态码，并有统一的错误返回数据结构（参见 ErrDetail）：

### 请求鉴权

某些接口请求时需要鉴权，有以下两种鉴权方式：

- 添加请求头 X-Sleepy-Secret，值为你在配置文件中定义的 secret
- 添加请求头 Authorization，先以 Bearer 开头，再空格接上配置文件中的 secret
"""

router = APIRouter(prefix="/api/v1", tags=["v1"])


@router.get(
    "",
    summary="测试存活",
    response_class=PlainTextResponse,
)
async def _():
    return "💤"


@router.get("/config/frontend", summary="获取前端配置")
async def _() -> FrontendConfig:
    """
    获取配置文件中 frontend 项下定义的数据
    """
    return config.frontend


async def get_info() -> Info:
    devices = (
        None
        if config.privacy_mode
        else {k: v.info for k, v in device_manager.devices.items()}
    )
    return Info(status=device_manager.overall_status, devices=devices)


@router.get("/info", summary="获取当前状态信息")
async def _() -> Info:
    """
    ### 实时获取

    使用 WebSocket 连接到该路径可以获取实时推送的状态
    """
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


def find_device_http(device_key: str) -> Device | None:
    device = device_manager.devices.get(device_key)
    if (
        (not device)
        and (not config.allow_new_devices)
        and (device_key not in config.devices)
    ):
        raise HTTPException(
            status_code=404,
            detail=f"Device '{device_key}' not found",
        )
    return device


async def add_device(
    device_key: str,
    info: DeviceInfoFromClient | None = None,
) -> Device:
    return device_manager.add(device_key, info or DeviceInfoFromClient())


@router.get(
    "/device/{device_key}/config",
    dependencies=[AuthDep],
    summary="获取设备配置",
    responses={
        200: {"model": OpSuccess},
        401: {"model": ErrDetail, "description": "鉴权失败"},
        404: {"model": ErrDetail, "description": "未找到设备"},
        422: {"model": ErrDetail, "description": "请求体解析失败"},
    },
)
async def _(
    device_key: str,
    exclude_unset: Annotated[bool, Query()] = False,
):
    if device_key in device_manager.devices:
        return device_manager.devices[device_key].config.model_dump(
            exclude_unset=exclude_unset,
        )
    if device_key in config.devices:
        return config.devices[device_key].model_dump(
            exclude_unset=exclude_unset,
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.put(
    "/device/{device_key}/config",
    dependencies=[AuthDep],
    summary="临时修改设备配置",
    responses={
        200: {"model": OpSuccess},
        201: {"model": OpSuccess},
        401: {"model": ErrDetail, "description": "鉴权失败"},
        404: {
            "model": ErrDetail,
            "description": "未找到设备，且服务端不允许添加新设备",
        },
        422: {"model": ErrDetail, "description": "请求体解析失败"},
    },
)
async def _(response: Response, device_key: str, new_config: DeviceConfig):
    device = find_device_http(device_key)
    if device:
        await device.update_config(new_config)
    else:
        response.status_code = status.HTTP_201_CREATED
    config.devices[device_key] = new_config
    return OpSuccess()


async def update_device_info_http(
    response: Response,
    device_key: str,
    info: DeviceInfoFromClient | None = None,
    is_replace: bool = False,
):
    device = find_device_http(device_key)
    if device:
        await device.update(info, replace=is_replace)
    else:
        device = await add_device(device_key, info)
        response.status_code = status.HTTP_201_CREATED
        await device.update()
    return device.info


@router.patch(
    "/device/{device_key}/info",
    dependencies=[AuthDep],
    summary="更新当前设备状态",
    responses={
        200: {"model": DeviceInfo},
        201: {"model": DeviceInfo},
        401: {"model": ErrDetail, "description": "鉴权失败"},
        404: {
            "model": ErrDetail,
            "description": "未在配置中找到设备，且服务端不允许添加新设备",
        },
        422: {"model": ErrDetail, "description": "请求体解析失败"},
    },
)
async def _(
    response: Response,
    device_key: str,
    info: DeviceInfoFromClient | None = None,
):
    """
    ### ⚠️ 注意！数据更新机制

    以 PATCH 方法调用此接口仅会更新你提交的部分数据，且为字典深度更新，也就是

    如果后端当前已存储以下数据：

    ```json
    {
        "name": "Sample Device",
        "description": "Device Description balabalabala",
        "data": {
            "current_app": {
                "name": "VSCode",
                "last_change_time": 1748524991530
            },
            "additional_statuses": [ "正在播放：結束バンド - Re:Re:", "喵呜喵呜~" ]
        }
    }
    ```

    你提交了以下数据：

    ```json
    {
        "description": "New description",
        "data": {
            "current_app": { "name": "IntelliJ IDEA" },
            "additional_statuses": [ "喵呜喵呜呜~" ]
        }
    }
    ```

    那么当前存储的数据将更新为：

    ```json
    {
        "name": "Sample Device",
        "description": "New description",
        "data": {
            "current_app": {
                "name": "IntelliJ IDEA",
                "last_change_time": 1748524991530
            },
            "additional_statuses": [ "喵呜喵呜呜~" ]
        }
    }
    ```

    ### 实时推送

    使用 WebSocket 连接到本路径可以实时推送设备状态，在推送一条状态以后会返回当前状态

    连接后推送一条状态设备才会被设置为在线，且保持连接时将一直考虑为设备在线

    当断开连接时，设备将被立即设为离线

    针对 WS 连接消息体中新增了一个 `replace` 字段，如设置为 `true` 则与 PUT 请求一样是替换设备状态

    ### 新设备连接

    当一个未在配置文件中定义 device_key 的设备连接时，其配置将设置为首次请求发送的数据

    ### 在线状态超时机制

    当某设备选择采用轮询请求该接口更新状态时，如果设备没有在后端配置文件定义的时间间隔内再次请求该接口，该设备将自动变为离线状态

    ### 仅保持唯一数据接收方式

    当某设备已通过 WebSocket 连接到后端，依然 HTTP 请求本接口，或新建一个 WebSocket 连接时，旧连接将自动断开
    """

    return await update_device_info_http(response, device_key, info, is_replace=False)


@router.put(
    "/device/{device_key}/info",
    dependencies=[AuthDep],
    summary="替换当前设备状态",
    responses={
        200: {"model": DeviceInfo},
        201: {"model": DeviceInfo},
        400: {"model": ErrDetail, "description": "新设备缺少设备初始配置"},
        401: {"model": ErrDetail, "description": "鉴权失败"},
        404: {
            "model": ErrDetail,
            "description": "未找到设备，且服务端不允许添加新设备",
        },
        422: {"model": ErrDetail, "description": "请求体解析失败"},
    },
)
async def _(
    response: Response,
    device_key: str,
    info: DeviceInfoFromClient | None = None,
):
    """
    ### ⚠️ 注意！数据更新机制

    以 PUT 方法请求本接口时，将会将 服务端当前设备配置 与 当前请求体 进行字典合并，之后完全替换当前设备信息

    如后端当前配置为：

    ```json
    {
        "name": "Sample Device",
        "description": "Device Description balabalabala",
    }
    ```

    当前存储数据为：

    ```json
    {
        "name": "Sample Device",
        "description": "Device Description balabalabala",
        "data": {
            "additional_statuses": [ "喵呜喵呜呜~" ]
        }
    }
    ```

    如果你提交下面数据：

    ```json
    {
        "description": "New description",
        "data": {}
    }
    ```

    那么当前存储数据将更新为：

    ```json
    {
        "name": "Sample Device",
        "description": "New description",
        "data": {}
    }
    ```

    ### 其他信息

    请参考 PATCH 方法的文档
    """

    return await update_device_info_http(response, device_key, info, is_replace=True)


@router.delete(
    "/device/{device_key}/info",
    dependencies=[AuthDep],
    summary="删除当前设备状态",
    responses={
        200: {"model": OpSuccess},
        401: {"model": ErrDetail, "description": "鉴权失败"},
        404: {"model": ErrDetail, "description": "未找到设备"},
        422: {"model": ErrDetail, "description": "请求体解析失败"},
    },
)
async def _(device_key: str):
    device = device_manager.devices.get(device_key)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device '{device_key}' not found",
        )
    await device_manager.remove(device_key)
    return OpSuccess()


async def close_ws_use_http_exc(ws: WebSocket, exc: HTTPException):
    we = WSErr(code=exc.status_code, detail=transform_exc_detail(exc.detail))
    await ws.close(
        code=status.WS_1008_POLICY_VIOLATION,
        reason=we.model_dump_json(exclude_unset=True),
    )


@router.websocket("/device/{device_key}/info", dependencies=[AuthDep])
async def _(ws: WebSocket, device_key: str):
    try:
        device = find_device_http(device_key)
    except HTTPException as e:
        await close_ws_use_http_exc(ws, e)
        return

    await ws.accept()
    if not device:
        try:
            data = await asyncio.wait_for(
                ws.receive_text(),
                timeout=config.poll_offline_timeout,
            )
        except TimeoutError:
            await close_ws_use_http_exc(
                ws,
                HTTPException(status.HTTP_408_REQUEST_TIMEOUT),
            )
            return

        try:
            device = await add_device(
                device_key,
                DeviceInfoFromClientWS.model_validate_json(data),
            )
            await device.update(in_long_conn=True)
        except Exception as e:
            logger.exception(f"WebSocket error while adding device '{device_key}'")
            code = (
                status.HTTP_422_UNPROCESSABLE_ENTITY
                if isinstance(e, ValidationError)
                else status.HTTP_400_BAD_REQUEST
            )
            await close_ws_use_http_exc(ws, HTTPException(code))
            return

    try:
        await device.handle_ws(ws)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.exception(f"WebSocket error while handling device '{device_key}'")
        code = (
            status.HTTP_422_UNPROCESSABLE_ENTITY
            if isinstance(e, ValidationError)
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        await close_ws_use_http_exc(ws, HTTPException(code))
