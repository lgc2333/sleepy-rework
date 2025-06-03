import sys
from pathlib import Path

APP_NAME = "Sleepy Rework Desktop Client"
APP_ID = "sleepy_rework_client_desktop"
APP_PKG_NAME = "top.lgc2333.sleepy_rework.client_desktop"

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
