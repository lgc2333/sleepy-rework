import sys
from pathlib import Path

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon
from qfluentwidgets import FluentWindow


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent: FluentWindow):
        super().__init__(parent)
        self.parent_ = parent

        icon_path = Path(__file__).parent / "assets" / "icon.png"
        self.setIcon(QIcon(str(icon_path)))
        self.setToolTip("Sleepy Rework")

        self.create_menu()

        self.activated.connect(self.on_tray_activated)

    def create_menu(self):
        menu = QMenu()

        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self.show_main_window)
        menu.addAction(show_action)

        quit_action = QAction("退出应用", self)
        quit_action.triggered.connect(self.quit_application)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def show_main_window(self):
        self.parent_.showNormal()
        self.parent_.activateWindow()

    def quit_application(self):
        sys.exit(0)

    def on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_main_window()
