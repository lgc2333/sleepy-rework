from typing import Any


# from pydantic.v1.utils
def deep_update[KT](
    mapping: dict[KT, Any],
    *updating_mappings: dict[KT, Any],
) -> dict[KT, Any]:
    updated_mapping = mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if (
                k in updated_mapping
                and isinstance(updated_mapping[k], dict)
                and isinstance(v, dict)
            ):
                updated_mapping[k] = deep_update(updated_mapping[k], v)
            else:
                updated_mapping[k] = v
    return updated_mapping
