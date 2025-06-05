from asyncio import Lock
from collections.abc import Callable, Coroutine
from typing import Any

from pydantic import BaseModel

type Co[T] = Coroutine[Any, Any, T]


# from pydantic.v1.utils
def deep_update[KT, VT, KS, VS](
    mapping: dict[KT, VT],
    *updating_mappings: dict[KS, VS],
) -> dict[KT | KS, VT | VS]:
    updated_mapping: dict[KT | KS, VT | VS] = mapping.copy()  # type: ignore
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if (
                k in updated_mapping
                and isinstance((u := updated_mapping[k]), dict)
                and isinstance(v, dict)
            ):
                updated_mapping[k] = deep_update(u, v)
            else:
                updated_mapping[k] = v
    return updated_mapping


def combine_model[M: BaseModel](target: M, **kwargs: Any) -> M:
    data = deep_update(target.model_dump(exclude_unset=True), kwargs)
    return target.model_validate(data)


def combine_model_from_model[M: BaseModel](target: M, source: BaseModel) -> M:
    return combine_model(target, **source.model_dump(exclude_unset=True))


def with_lock[**P, R](lock: Lock):
    def deco(func: Callable[P, Co[R]]) -> Callable[P, Co[R]]:
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            async with lock:
                return await func(*args, **kwargs)

        return wrapper

    return deco
