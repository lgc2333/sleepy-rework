from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.staticfiles import StaticFiles

from . import __version__, api_v1
from .config import config
from .exc_handle import install_exc_handlers
from .log import logger

DESCRIPTION = f"""
{api_v1.DESCRIPTION}
"""


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.debug(f"Starting app with config: {config.model_dump_json()}")
    yield


app = FastAPI(
    title="Sleepy Rework Backend",
    description=DESCRIPTION,
    version=__version__,
    lifespan=lifespan,
    openapi_url=f"{config.docs_url}/openapi.json" if config.docs_url else None,
    docs_url=f"{config.docs_url}" if config.docs_url else None,
    redoc_url=f"{config.docs_url}/redoc" if config.docs_url else None,
    swagger_ui_oauth2_redirect_url=(
        f"{config.docs_url}/oauth2-redirect" if config.docs_url else None
    ),
)

if config.app.ssl_keyfile:
    app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    CORSMiddleware,
    **config.cors.model_dump(),
)

install_exc_handlers(app)

app.include_router(api_v1.router)
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
