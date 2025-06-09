import subprocess
import sys

# from sleepy_rework_client_desktop import __version__ as version

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
