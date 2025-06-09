import json
from pathlib import Path

openapi_json = json.loads(
    (Path.cwd() / "openapi.json").read_text(encoding="u8"),
)

schemas = openapi_json.get("components", {}).get("schemas", {}).keys()

with (Path.cwd() / "src" / "base.ts").open("w", encoding="u8") as f:
    f.write("import type { components } from './openapi'\n\n")
    for schema in schemas:
        f.write(f"export type {schema} = components['schemas']['{schema}']\n")
