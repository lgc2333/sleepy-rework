import asyncio
import sys
from typing import override

import qasync
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QCloseEvent, QIcon, QShowEvent
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import (
    FluentIcon,
    MSFluentWindow,
    SplashScreen,
    SystemThemeListener,
    qconfig,
)

from .assets import ICON_PATH
from .config import APP_NAME, config, reApplyThemeColor, reApplyThemeMode
from .utils.common import AUTO_START_OPT
from .utils.single_app import QtSingleApplication


class MainWindow(MSFluentWindow):
    def __init__(self, show: bool = True):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(900, 650)

        self.setWindowIcon(QIcon(str(ICON_PATH)))

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(128, 128))
        if show:
            self.show()

        self.setupTrayIcon()
        self.setupThemeListener()
        self.setupUI()
        self.restoreAutoStart()
        self.setupClient()

        self.splashScreen.finish()

    def setupTrayIcon(self):
        from .tray import SystemTrayIcon

        self.trayIcon = SystemTrayIcon(self, self.windowIcon())
        self.trayIcon.show()

    def setupThemeListener(self):
        self.themeListener = SystemThemeListener(self)
        self.themeListener.systemThemeChanged.connect(reApplyThemeMode)
        self.themeListener.systemThemeChanged.connect(reApplyThemeColor)
        self.themeListener.start()

    def setupUI(self):
        from .views import HomePage, SettingsPage

        self.homePage = HomePage()
        self.addSubInterface(
            self.homePage,
            FluentIcon.HOME,
            "主页",
            FluentIcon.HOME_FILL,
        )

        self.settingsPage = SettingsPage()
        self.addSubInterface(
            self.settingsPage,
            FluentIcon.SETTING,
            "设置",
        )

        self.navigationInterface.setCurrentItem(self.homePage.routeKey)

    def restoreAutoStart(self):
        from .utils.auto_start import AutoStartManager

        if not AutoStartManager:
            return

        config_auto_start_enabled: bool = qconfig.get(config.appAutoStart)
        auto_start_enabled = AutoStartManager.is_enabled()
        if auto_start_enabled == config_auto_start_enabled:
            return

        res = (
            AutoStartManager.disable()
            if auto_start_enabled
            else AutoStartManager.enable()
        )
        if res:
            return
        print(f"Failed to restore autostart setting to {config_auto_start_enabled}")
        qconfig.set(config.appAutoStart, auto_start_enabled)

    @override
    def setupClient(self):
        from .client.info import info_feeder

        if qconfig.get(config.serverEnableConnect):
            info_feeder.run_in_background()

    @override
    def showEvent(self, a0: QShowEvent | None):
        # reApplyThemeMode()
        reApplyThemeColor()
        super().showEvent(a0)

    @override
    def closeEvent(self, a0: QCloseEvent | None):  # noqa: N802
        if not a0:
            return

        if self.trayIcon.isVisible():
            self.hide()
            a0.ignore()
            return

        if hasattr(self, "themeListener"):
            self.themeListener.terminate()
            self.themeListener.deleteLater()
        a0.accept()


def launch():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough,
    )
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QtSingleApplication("sleepy_rework_desktop_client", sys.argv)

    if app.isRunning():
        print("Another instance is already running.")
        app.sendMessage("114514")
        sys.exit(0)

    app.setQuitOnLastWindowClosed(False)

    event_loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(event_loop)

    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)

    window = MainWindow(
        show=not (
            (AUTO_START_OPT in sys.argv) and qconfig.get(config.appStartMinimized)
        ),
    )
    app.setActivationWindow(window)

    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())
