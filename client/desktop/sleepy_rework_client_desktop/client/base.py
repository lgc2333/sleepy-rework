import asyncio
import contextlib
from asyncio import Task
from typing import Any, Literal, Self, cast, overload

from websockets import ClientConnection, connect

from ..utils.common import SafeLoggedSignal


class RetryWSClient[D: str | bytes]:
    @overload
    def __init__(
        self: "RetryWSClient[bytes]",
        endpoint: str,
        *,
        retry_sleep: int = ...,
        decode: Literal[False],
        **kwargs,
    ) -> None: ...
    @overload
    def __init__(
        self: "RetryWSClient[str]",
        endpoint: str,
        *,
        retry_sleep: int = ...,
        decode: Literal[True] = True,
        **kwargs,
    ) -> None: ...
    @overload
    def __init__(
        self: "RetryWSClient[str|bytes]",
        endpoint: str,
        *,
        retry_sleep: int = ...,
        decode: bool,
        **kwargs,
    ) -> None: ...
    def __init__(
        self,
        endpoint: str,
        *,
        retry_sleep: int = 3,
        decode: bool = True,
        proxy: str | Literal[True] | None = None,
        **kwargs,
    ):
        self.retry_sleep: int = retry_sleep
        self.connect_kwargs = kwargs

        self._endpoint: str = endpoint
        self._decode: bool = decode
        self._proxy: str | Literal[True] | None = proxy

        self._ws: ClientConnection | None = None
        self._run_task: Task | None = None

        self.on_connect_error = SafeLoggedSignal[[Self, Exception], Any]()
        self.on_connected = SafeLoggedSignal[[Self], Any]()
        self.on_disconnected = SafeLoggedSignal[[Self, Exception], Any]()
        self.on_message = SafeLoggedSignal[[Self, D], Any]()
        self.on_background_started = SafeLoggedSignal[[Self], Any]()
        self.on_background_stopped = SafeLoggedSignal[[Self], Any]()

    def close_ws(self):
        ws = self._ws
        if ws:
            asyncio.create_task(ws.close())

    @property
    def ws(self):
        if not self._ws:
            raise RuntimeError("WebSocket not connected")
        return self._ws

    @property
    def connected(self):
        return bool(self._ws)

    @property
    def decode(self) -> bool:
        return self._decode

    @property
    def endpoint(self) -> str:
        return self._endpoint

    @endpoint.setter
    def endpoint(self, value: str):
        self._endpoint = value
        self.close_ws()

    @property
    def proxy(self) -> str | Literal[True] | None:
        return self._proxy

    @proxy.setter
    def proxy(self, value: str | Literal[True] | None):
        self._proxy = value
        self.close_ws()

    async def _handle_ws(self, ws: ClientConnection):
        self._ws = ws
        self.on_connected.task_gather(self)
        while True:
            try:
                msg = cast("D", await ws.recv(decode=self._decode))
            except Exception as e:
                print(f"WebSocket disconnected: {e}")
                self._ws = None
                self.on_disconnected.task_gather(self, e)
                break
            else:
                self.on_message.task_gather(self, msg)

    async def _run(self):
        while True:
            try:
                ws = await connect(
                    self._endpoint,
                    proxy=self._proxy,
                    **self.connect_kwargs,
                )
            except Exception as e:
                print(f"WebSocket connection error: {e}")
                self.on_connect_error.task_gather(self, e)
            else:
                async with ws:
                    await self._handle_ws(ws)
            await asyncio.sleep(self.retry_sleep)

    async def wait_message(self) -> D:
        fut = asyncio.Future()

        @self.on_message.connect
        async def cb(_: Self, msg: D):
            self.on_message.slots.remove(cb)
            fut.set_result(msg)

        return await fut

    def _task_cleanup(self, task: Task):
        if self._run_task is task:
            self._run_task = None
        self.on_background_stopped.task_gather(self)

    def run_in_background(self):
        if self._run_task is None:
            task = Task(self._run())
            self._run_task = task
            self._run_task.add_done_callback(lambda _: self._task_cleanup(task))
            self.on_background_started.task_gather(self)
        return self._run_task

    def _stop_background(self) -> Task | None:
        if self._run_task is None:
            return None
        task = self._run_task
        task.cancel()
        return task

    def stop_background(self):
        self._stop_background()

    async def stop_background_wait(self):
        task = self._stop_background()
        if not task:
            return
        with contextlib.suppress(Exception):
            await task
