from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.staticfiles import StaticFiles

from .config import config

app = FastAPI()

if config.app.ssl_keyfile:
    app.add_middleware(HTTPSRedirectMiddleware)

app.add_middleware(
    CORSMiddleware,
    **config.cors.model_dump(),
)


@app.get("/none")
async def _():
    return Response(status_code=204)


app.mount(
    "/",
    StaticFiles(
        directory=(
            config.static_dir
            if config.static_dir
            else (Path(__file__).parent / "static")
        ),
        html=True,
    ),
    name="static",
)
