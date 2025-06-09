from typing import override

from PySide6.QtCore import QSize
from PySide6.QtGui import QCloseEvent, QIcon, QShowEvent
from qfluentwidgets import (
    FluentIcon,
    MSFluentWindow,
    SplashScreen,
    SystemThemeListener,
    qconfig,
)

from .assets import ICON_PATH
from .config import config, reApplyThemeColor, reApplyThemeMode
from .consts import APP_NAME


class MainWindow(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(900, 650)
        self.setWindowIcon(QIcon(str(ICON_PATH)))

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(128, 128))

    def setup(self):
        self.setupTrayIcon()
        self.setupThemeListener()
        self.setupUI()
        self.restoreAutoStart()
        self.setupInfoClient()
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

    def setupInfoClient(self):
        from .utils.activity import activity_detector
        from .utils.client.info import info_feeder

        if qconfig.get(config.serverEnableConnect):
            info_feeder.run_in_background()

        activity_detector.setup()

    @override
    def showEvent(self, a0: QShowEvent):
        # reApplyThemeMode()
        reApplyThemeColor()
        super().showEvent(a0)

    @override
    def closeEvent(self, a0: QCloseEvent):  # noqa: N802
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
