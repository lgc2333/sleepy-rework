from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cached_property, partial
from types import EllipsisType, TracebackType
from typing import Any, Never, Self, override

from httpx import AsyncClient, Client, HTTPStatusError, Response
from httpx._client import USER_AGENT as UA_BASE
from pydantic import BaseModel

from ..config import DeviceConfig, FrontendConfig
from ..models import DeviceInfo, ErrDetail, Info, OpSuccess
from .types import AsyncHttpApi, SyncHttpApi


@dataclass
class ParamInfo:
    name: str
    type_anno: str
    default: Any | EllipsisType = ...
    default_type_anno: str = "..."


@dataclass
class BodyInfo:
    type_anno: str
    default: Any | EllipsisType = ...
    default_type_anno: str = "..."


@dataclass
class ResponseInfo:
    model: type[BaseModel] | type[str] | type[bytes]
    type_anno: str


@dataclass
class HttpApiInfo:
    method: str
    endpoint: str
    path_params: dict[str, ParamInfo] = field(default_factory=dict)
    query_params: dict[str, ParamInfo] = field(default_factory=dict)
    body: BodyInfo | None = None  # model is ignored
    response: ResponseInfo | None = None  # default is ignored


HTTP_APIS: dict[str, HttpApiInfo] = {
    "test_alive": HttpApiInfo(
        method="GET",
        endpoint="/api/v1",
        response=ResponseInfo(
            model=str,
            type_anno="str",
        ),
    ),
    "get_frontend_config": HttpApiInfo(
        method="GET",
        endpoint="/api/v1/config/frontend",
        response=ResponseInfo(
            model=FrontendConfig,
            type_anno="m.FrontendConfig",
        ),
    ),
    "get_info": HttpApiInfo(
        method="GET",
        endpoint="/api/v1/info",
        response=ResponseInfo(
            model=Info,
            type_anno="m.Info",
        ),
    ),
    "get_device_config": HttpApiInfo(
        method="GET",
        endpoint="/api/v1/device/{device_key}/config",
        path_params={
            "device_key": ParamInfo(
                name="device_key",
                type_anno="str",
            ),
        },
        response=ResponseInfo(
            model=DeviceConfig,
            type_anno="m.DeviceConfig",
        ),
    ),
    "put_device_config": HttpApiInfo(
        method="PUT",
        endpoint="/api/v1/device/{device_key}/config",
        path_params={
            "device_key": ParamInfo(
                name="device_key",
                type_anno="str",
            ),
        },
        body=BodyInfo(
            type_anno="m.DeviceConfig",
        ),
        response=ResponseInfo(
            model=OpSuccess,
            type_anno="m.OpSuccess",
        ),
    ),
    "patch_device_info": HttpApiInfo(
        method="PATCH",
        endpoint="/api/v1/device/{device_key}/info",
        path_params={
            "device_key": ParamInfo(
                name="device_key",
                type_anno="str",
            ),
        },
        body=BodyInfo(
            type_anno="m.DeviceInfoFromClient | None",
            default=None,
            default_type_anno="None",
        ),
        response=ResponseInfo(
            model=DeviceInfo,
            type_anno="m.DeviceInfo",
        ),
    ),
    "put_device_info": HttpApiInfo(
        method="PUT",
        endpoint="/api/v1/device/{device_key}/info",
        path_params={
            "device_key": ParamInfo(
                name="device_key",
                type_anno="str",
            ),
        },
        body=BodyInfo(
            type_anno="m.DeviceInfoFromClient | None",
            default=None,
            default_type_anno="None",
        ),
        response=ResponseInfo(
            model=DeviceInfo,
            type_anno="m.DeviceInfo",
        ),
    ),
    "delete_device_info": HttpApiInfo(
        method="DELETE",
        endpoint="/api/v1/device/{device_key}/info",
        path_params={
            "device_key": ParamInfo(
                name="device_key",
                type_anno="str",
            ),
        },
        response=ResponseInfo(
            model=OpSuccess,
            type_anno="m.OpSuccess",
        ),
    ),
}


class APIError(Exception):
    def __init__(self, status: int, detail: ErrDetail) -> None:
        super().__init__()
        self.status = status
        self.e = detail

    def __str__(self) -> str:
        parts: list[str] = [f"[{self.status}]"]
        if self.e.type:
            parts.append(f"({self.e.type})")
        if self.e.msg:
            parts.append(f"{self.e.msg}")
        return " ".join(parts)


class BaseHttpApiClient(ABC):
    def __init__(
        self,
        base_url: str,
        secret: str | None = None,
        app_ua: str | None = None,
        **kwargs: Any,
    ):
        self.base_url = base_url
        self.secret = secret
        self.app_ua = app_ua
        self.__post_init__(**kwargs)

    def __post_init__(self, **kwargs: Any):
        return None

    def collect_params(
        self,
        params: dict[str, ParamInfo],
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        collected = {}
        for param, info in params.items():
            if (param not in kwargs) and (info.default is Ellipsis):
                raise ValueError(f"Missing required parameter: {param}")
            v = kwargs.get(param, info.default)
            collected[param] = v
        return collected

    def collect_body(self, body: BodyInfo | None, args: tuple[Any, ...]) -> Any:
        if body:
            if (body.default is Ellipsis) and (not args):
                raise ValueError("Body required for this API")
            if len(args) > 1:
                raise ValueError("Only one body argument should be passed")
            obj = args[0] if args else body.default
        elif args:
            raise ValueError("This API does not accept body arguments")
        else:
            obj = None

        if obj and isinstance(obj, BaseModel):
            obj = obj.model_dump()

        return obj

    @cached_property
    def headers(self) -> dict[str, str]:
        from .. import __version__

        headers = {"User-Agent": f"{UA_BASE} sleepy-rework-types/{__version__}"}
        if self.secret:
            headers["Authorization"] = f"Bearer {self.secret}"
        if self.app_ua:
            headers["User-Agent"] = f"{self.app_ua} {headers['User-Agent']}"
        return headers

    def handle_status_err(self, e: HTTPStatusError) -> Never:
        raise APIError(
            e.response.status_code,
            ErrDetail.model_validate_json(e.response.content),
        ) from e

    def validate_resp(self, resp: Response, info: ResponseInfo | None):
        if not info:
            return None
        if issubclass(info.model, str):
            return resp.text
        if issubclass(info.model, bytes):
            return resp.content
        return info.model.model_validate_json(resp.content)

    @abstractmethod
    def request(
        self,
        method: str,
        endpoint: str,
        query_params: dict[str, Any],
        body: Any,
        resp_info: ResponseInfo | None,
    ) -> Any: ...

    def request_from_info(
        self,
        api_info: HttpApiInfo,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        endpoint = api_info.endpoint
        path_params = self.collect_params(api_info.path_params, kwargs)
        endpoint = endpoint.format(**path_params)

        query_params = self.collect_params(api_info.query_params, kwargs)
        body = self.collect_body(api_info.body, args)

        return self.request(
            method=api_info.method,
            endpoint=endpoint,
            query_params=query_params,
            body=body,
            resp_info=api_info.response,
        )

    def __getattr__(self, name: str, /) -> Callable[..., Any]:
        if name.startswith("_") or not (api_info := HTTP_APIS.get(name)):
            return super().__getattribute__(name)
        return partial(self.request_from_info, api_info)


class SyncHttpApiClient(BaseHttpApiClient, SyncHttpApi):
    @override
    def __post_init__(self):
        super().__post_init__()
        self._client: Client | None = None

    def get_client(self) -> Client:
        if not self._client:
            self._client = Client(
                base_url=self.base_url,
                headers=self.headers,
                follow_redirects=True,
                http2=True,
            )
        return self._client

    def __enter__(self) -> Self:
        self.get_client().__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        cli = self.get_client()
        self._client = None
        return cli.__exit__(exc_type, exc_value, traceback)

    @override
    def request(
        self,
        method: str,
        endpoint: str,
        query_params: dict[str, Any],
        body: Any,
        resp_info: ResponseInfo | None,
    ) -> Any:
        try:
            resp = (
                self.get_client()
                .request(method, endpoint, params=query_params, json=body)
                .raise_for_status()
            )
        except HTTPStatusError as e:
            self.handle_status_err(e)
        return self.validate_resp(resp, resp_info)


class AsyncHttpApiClient(BaseHttpApiClient, AsyncHttpApi):
    @override
    def __post_init__(self):
        super().__post_init__()
        self._client: AsyncClient | None = None

    def get_client(self) -> AsyncClient:
        if not self._client:
            self._client = AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                follow_redirects=True,
                http2=True,
            )
        return self._client

    async def __aenter__(self) -> Self:
        await self.get_client().__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        cli = self.get_client()
        self._client = None
        return await cli.__aexit__(exc_type, exc_value, traceback)

    @override
    async def request(
        self,
        method: str,
        endpoint: str,
        query_params: dict[str, Any],
        body: Any,
        resp_info: ResponseInfo | None,
    ) -> Any:
        try:
            resp = (
                await self.get_client().request(
                    method,
                    endpoint,
                    params=query_params,
                    json=body,
                )
            ).raise_for_status()
        except HTTPStatusError as e:
            self.handle_status_err(e)
        return self.validate_resp(resp, resp_info)
