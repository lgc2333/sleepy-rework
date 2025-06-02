import sys
from typing import override

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import MSFluentWindow, SplashScreen, qconfig

from .assets import ICON_PATH
from .config import config
from .single_app import QtSingleApplication
from .utils.auto_start import AutoStartManager
from .utils.common import AUTO_START_OPT


class MainWindow(MSFluentWindow):
    def __init__(self, show: bool = True):
        super().__init__()
        self.setWindowTitle("Sleepy Rework")
        self.resize(900, 650)

        self.setWindowIcon(QIcon(str(ICON_PATH)))

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(128, 128))
        if show:
            self.show()

        self.setupTrayIcon()
        self.setupUI()

        self.splashScreen.finish()

    def setupTrayIcon(self):
        from .tray import SystemTrayIcon

        self.trayIcon = SystemTrayIcon(self)
        self.trayIcon.show()

    def setupUI(self):
        from qfluentwidgets import FluentIcon

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

    @override
    def closeEvent(self, a0: QCloseEvent | None):  # noqa: N802
        if not a0:
            return

        if self.trayIcon.isVisible():
            self.hide()
            a0.ignore()
        else:
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

    if AutoStartManager:
        config_auto_start_enabled: bool = qconfig.get(config.appAutoStart)
        auto_start_enabled = AutoStartManager.is_enabled()
        if auto_start_enabled != config_auto_start_enabled:
            res = (
                AutoStartManager.disable()
                if auto_start_enabled
                else AutoStartManager.enable()
            )
            if not res:
                qconfig.set(config.appAutoStart, auto_start_enabled)

    window = MainWindow(
        show=not (
            (AUTO_START_OPT in sys.argv) and qconfig.get(config.appStartMinimized)
        ),
    )
    app.setActivationWindow(window)

    sys.exit(app.exec_())
