import json
from pathlib import Path

from sleepy_rework.app import app

(Path.cwd() / "openapi.json").write_text(
    json.dumps(
        app.openapi(),
        indent=2,
        ensure_ascii=False,
    ),
    encoding="u8",
)
