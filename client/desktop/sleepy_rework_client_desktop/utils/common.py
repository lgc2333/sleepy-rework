import sys
import traceback
from pathlib import Path

from cookit import Signal

AUTO_START_OPT = "--auto-start"


def get_start_args(auto_start: bool = True) -> list[str]:
    args = []
    if getattr(sys, "frozen", False):
        args.append(sys.executable)
    else:
        assert __package__
        p_exec = Path(sys.executable)
        if "python" in p_exec.name:
            pw_exec = p_exec.with_name(p_exec.name.replace("python", "pythonw", 1))
            if pw_exec.exists():
                p_exec = pw_exec
        args.extend([str(p_exec), "-m", __package__.split(".")[0]])
    if auto_start:
        args.append(AUTO_START_OPT)
    return args


async def signal_exc_handler(_: Signal, e: Exception) -> Exception:
    traceback.print_exception(e)
    return e


class SafeLoggedSignal[**A, R](Signal[A, R, Exception]):
    def __init__(self) -> None:
        super().__init__(signal_exc_handler)


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
