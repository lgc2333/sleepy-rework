import subprocess
import sys
from pathlib import Path

# from sleepy_rework_client_desktop import __version__ as version

BUILD_CONF_PATH = (
    Path(__file__).parent.parent
    / "client/desktop/sleepy_rework_client_desktop/_build_conf.py"
)
commit_hash = subprocess.run(
    ("git", "rev-parse", "--short", "HEAD"),
    check=True,
    stdout=subprocess.PIPE,
    encoding="u8",
).stdout.strip()
BUILD_CONF_PATH.write_text(
    f'commit_hash = "{commit_hash}"\n',
    "u8",
)

# a = [
#     sys.executable,
#     *("-m", "nuitka"),
#     "client/desktop/main.py",
#     # Nuitka options
#     "--onefile",
#     "--plugin-enable=pyside6",
#     "--include-package-data=sleepy_rework_client_desktop",
#     # metadata
#     "--product-name=Sleepy Rework Desktop Client",
#     f"--product-version={version}",
#     # windows
#     "--windows-icon-from-ico=client/desktop/sleepy_rework_client_desktop/assets/icon.png",
#     "--windows-console-mode=disable",
#     # macOS
#     "--macos-create-app-bundle",
#     "--macos-app-icon=client/desktop/sleepy_rework_client_desktop/assets/icon.png",
# ]
# if sys.platform == "win32":
#     a.append("--msvc=latest")

a = [
    sys.executable,
    *("-m", "PyInstaller"),
    "--onefile",
    "--windowed",
    *("--icon", "../client/desktop/sleepy_rework_client_desktop/assets/icon.png"),
    *("--name", "Sleepy Rework Desktop Client"),
    *("--specpath", "build"),
    *("--collect-all", "sleepy_rework_client_desktop"),
    "client/desktop/main.py",
]

subprocess.run(a, check=False)  # noqa: S603
