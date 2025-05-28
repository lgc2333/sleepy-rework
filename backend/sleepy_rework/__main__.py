import uvicorn

from .config import config


def start():
    uvicorn.run(
        "sleepy_rework.app:app",
        host=str(config.app.host),
        **config.app.model_dump(exclude={"host"}),
    )


if __name__ == "__main__":
    start()
