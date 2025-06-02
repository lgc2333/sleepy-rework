import sys
from pathlib import Path

AUTO_START_OPT = "--auto-start"


def get_start_args(auto_start: bool = True) -> list[str]:
    args = []
    if getattr(sys, "frozen", False):
        args.append(sys.executable)
    else:
        assert __package__
        p_exec = Path(sys.executable)
        pw_exec = p_exec.with_stem(f"{p_exec.stem}w")
        if pw_exec.exists():
            p_exec = pw_exec
        args.extend([str(p_exec), "-m", __package__.split(".")[0]])
    if auto_start:
        args.append(AUTO_START_OPT)
    return args
