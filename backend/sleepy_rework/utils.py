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


def update_model(target: BaseModel, **kwargs: Any) -> BaseModel:
    updated_data = target.model_dump(exclude_unset=True)
    updated_data.update(kwargs)
    return target.model_validate(updated_data)


def update_model_from_model[M: BaseModel](target: M, source: BaseModel) -> M:
    updated_data = target.model_dump(exclude_unset=True)
    updated_data.update(source.model_dump(exclude_unset=True))
    return target.model_validate(updated_data)
