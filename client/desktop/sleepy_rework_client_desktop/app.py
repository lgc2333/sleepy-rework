import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentIcon, MSFluentWindow

from .tray import SystemTrayIcon
from .views.home import HomePage


class MainWindow(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sleepy Rework")
        self.resize(900, 650)

        icon_path = Path(__file__).parent / "assets" / "icon.png"
        self.setWindowIcon(QIcon(str(icon_path)))

        self.init_ui()

        self.tray_icon = SystemTrayIcon(self)
        self.tray_icon.show()

    def init_ui(self):
        self.home_page = HomePage()
        self.addSubInterface(
            self.home_page,
            FluentIcon.HOME,
            "主页",
            FluentIcon.HOME_FILL,
        )

        self.navigationInterface.setCurrentItem(self.home_page.route_key)

    def closeEvent(self, a0: QCloseEvent | None):  # noqa: N802
        if not a0:
            return
        if self.tray_icon.isVisible():
            self.hide()
            a0.ignore()
        else:
            a0.accept()


def launch():
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
