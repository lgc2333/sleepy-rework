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
    ) -> None: ...
    @overload
    def __init__(
        self: "RetryWSClient[str]",
        endpoint: str,
        *,
        retry_sleep: int = ...,
        decode: Literal[True] = True,
    ) -> None: ...
    @overload
    def __init__(
        self: "RetryWSClient[str|bytes]",
        endpoint: str,
        *,
        retry_sleep: int = ...,
        decode: bool,
    ) -> None: ...
    def __init__(
        self,
        endpoint: str,
        *,
        retry_sleep: int = 5,
        decode: bool = True,
    ):
        self.endpoint = endpoint
        self.retry_sleep = retry_sleep
        self.decode = decode

        self._ws: ClientConnection | None = None
        self._run_task: Task | None = None

        self.on_connect_error = SafeLoggedSignal[[Self, Exception], Any]()
        self.on_connected = SafeLoggedSignal[[Self], Any]()
        self.on_disconnected = SafeLoggedSignal[[Self, Exception], Any]()
        self.on_message = SafeLoggedSignal[[Self, D], Any]()
        self.on_background_started = SafeLoggedSignal[[Self], Any]()
        self.on_background_stopped = SafeLoggedSignal[[Self], Any]()

    @property
    def ws(self):
        return self._ws

    @property
    def connected(self):
        return bool(self._ws)

    async def _handle_ws(self, ws: ClientConnection):
        self._ws = ws
        self.on_connected.task_gather(self)
        while True:
            try:
                msg = cast("D", await ws.recv(decode=self.decode))
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
                ws = await connect(self.endpoint)
            except Exception as e:
                print(f"WebSocket connection error: {e}")
                self.on_connect_error.task_gather(self, e)
            else:
                async with ws:
                    await self._handle_ws(ws)
            await asyncio.sleep(self.retry_sleep)

    def _task_cleanup(self):
        self._run_task = None
        self.on_background_stopped.task_gather(self)

    def run_in_background(self):
        if self._run_task is None:
            self._run_task = Task(self._run())
            self._run_task.add_done_callback(lambda _: self._task_cleanup())
            self.on_background_started.task_gather(self)
        return self._run_task

    def _stop_background(self) -> Task | None:
        if self._run_task is None:
            return None
        task = self._run_task
        self._task_cleanup()
        return task

    def stop_background(self):
        self._stop_background()

    async def stop_background_wait(self):
        task = self._stop_background()
        if not task:
            return
        with contextlib.suppress(Exception):
            await task
