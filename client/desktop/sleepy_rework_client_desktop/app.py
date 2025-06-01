import sys
from pathlib import Path
from typing import override

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import MSFluentWindow, SplashScreen

from .config import config  # noqa: F401
from .single_app import QtSingleApplication


class MainWindow(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sleepy Rework")
        self.resize(900, 650)

        icon_path = Path(__file__).parent / "assets" / "icon.png"
        self.setWindowIcon(QIcon(str(icon_path)))

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(128, 128))
        self.show()

        self.init_tray_icon()
        self.init_ui()

        self.splashScreen.finish()

    def init_tray_icon(self):
        from .tray import SystemTrayIcon

        self.tray_icon = SystemTrayIcon(self)
        self.tray_icon.show()

    def init_ui(self):
        from qfluentwidgets import FluentIcon

        from .views import HomePage, SettingsPage

        self.home_page = HomePage()
        self.addSubInterface(
            self.home_page,
            FluentIcon.HOME,
            "主页",
            FluentIcon.HOME_FILL,
        )

        self.settings_page = SettingsPage()
        self.addSubInterface(
            self.settings_page,
            FluentIcon.SETTING,
            "设置",
        )

        self.navigationInterface.setCurrentItem(self.home_page.route_key)

    @override
    def closeEvent(self, a0: QCloseEvent | None):  # noqa: N802
        if not a0:
            return

        if self.tray_icon.isVisible():
            self.hide()
            a0.ignore()
        else:
            a0.accept()


def launch():
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QtSingleApplication("sleepy_rework_desktop_client", sys.argv)

    if app.isRunning():
        print("Another instance is already running.")
        app.sendMessage("activate")
        sys.exit(0)

    app.setQuitOnLastWindowClosed(False)

    window = MainWindow()
    app.setActivationWindow(window)

    sys.exit(app.exec_())
