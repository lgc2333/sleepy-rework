import sys

FROZEN: bool = getattr(sys, "frozen", False)

APP_NAME = "Sleepy Rework Desktop Client"
APP_NAME_NO_SPACE = "SleepyReworkDesktopClient"
APP_ID = "sleepy_rework_client_desktop"
APP_PKG_NAME = "top.lgc2333.sleepy_rework.client_desktop"

if not FROZEN:
    APP_NAME += " [DEV]"
    APP_NAME_NO_SPACE += "-Dev"
    APP_ID += "-dev"
    APP_PKG_NAME += ".dev"
