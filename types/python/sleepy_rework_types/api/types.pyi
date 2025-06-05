import typing as t

import sleepy_rework_types as m

class SyncHttpApi:
    def test_alive(self) -> str: ...
    def get_frontend_config(self) -> m.FrontendConfig: ...
    def get_info(self) -> m.Info: ...
    def update_device_info(
        self,
        body: m.DeviceInfoFromClient | None = None,
        /,
        *,
        device_key: str,
    ) -> m.OpSuccess: ...

class AsyncHttpApi:
    def test_alive(self) -> t.Coroutine[t.Any, t.Any, str]: ...
    def get_frontend_config(self) -> t.Coroutine[t.Any, t.Any, m.FrontendConfig]: ...
    def get_info(self) -> t.Coroutine[t.Any, t.Any, m.Info]: ...
    def update_device_info(
        self,
        body: m.DeviceInfoFromClient | None = None,
        /,
        *,
        device_key: str,
    ) -> t.Coroutine[t.Any, t.Any, m.OpSuccess]: ...
