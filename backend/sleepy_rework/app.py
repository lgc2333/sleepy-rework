from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors.allow_origins,
    allow_methods=config.cors.allow_methods,
    allow_headers=config.cors.allow_headers,
    allow_credentials=config.cors.allow_credentials,
    allow_origin_regex=config.cors.allow_origin_regex,
    expose_headers=config.cors.expose_headers,
    max_age=config.cors.max_age,
)


@app.get("/")
async def root():
    return {"message": "欢迎使用Sleepy Rework API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
