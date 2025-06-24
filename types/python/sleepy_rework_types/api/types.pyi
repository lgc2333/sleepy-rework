import typing as t

import sleepy_rework_types as m

class SyncHttpApi:
    def test_alive(self) -> str: ...
    def get_frontend_config(self) -> m.FrontendConfig: ...
    def get_info(self) -> m.Info: ...
    def get_device_config(self, *, device_key: str) -> m.DeviceConfig: ...
    def put_device_config(
        self,
        body: m.DeviceConfig,
        /,
        *,
        device_key: str,
    ) -> m.OpSuccess: ...
    def patch_device_info(
        self,
        body: m.DeviceInfoFromClient | None = None,
        /,
        *,
        device_key: str,
    ) -> m.DeviceInfo: ...
    def put_device_info(
        self,
        body: m.DeviceInfoFromClient | None = None,
        /,
        *,
        device_key: str,
    ) -> m.DeviceInfo: ...
    def delete_device_info(self, *, device_key: str) -> m.OpSuccess: ...

class AsyncHttpApi:
    def test_alive(self) -> t.Coroutine[t.Any, t.Any, str]: ...
    def get_frontend_config(self) -> t.Coroutine[t.Any, t.Any, m.FrontendConfig]: ...
    def get_info(self) -> t.Coroutine[t.Any, t.Any, m.Info]: ...
    def get_device_config(
        self,
        *,
        device_key: str,
    ) -> t.Coroutine[t.Any, t.Any, m.DeviceConfig]: ...
    def put_device_config(
        self,
        body: m.DeviceConfig,
        /,
        *,
        device_key: str,
    ) -> t.Coroutine[t.Any, t.Any, m.OpSuccess]: ...
    def patch_device_info(
        self,
        body: m.DeviceInfoFromClient | None = None,
        /,
        *,
        device_key: str,
    ) -> t.Coroutine[t.Any, t.Any, m.DeviceInfo]: ...
    def put_device_info(
        self,
        body: m.DeviceInfoFromClient | None = None,
        /,
        *,
        device_key: str,
    ) -> t.Coroutine[t.Any, t.Any, m.DeviceInfo]: ...
    def delete_device_info(
        self,
        *,
        device_key: str,
    ) -> t.Coroutine[t.Any, t.Any, m.OpSuccess]: ...
