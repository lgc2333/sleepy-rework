from typing import Any

from pydantic import BaseModel


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


def combine_model[M: BaseModel](target: M, **kwargs: Any) -> M:
    data = deep_update(target.model_dump(exclude_unset=True), kwargs)
    return target.model_validate(data)


def combine_model_from_model[M: BaseModel](target: M, source: BaseModel) -> M:
    return combine_model(target, **source.model_dump(exclude_unset=True))
