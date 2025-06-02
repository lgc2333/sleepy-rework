import sys
from pathlib import Path

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QWidget
from qfluentwidgets import Action


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.parent_ = parent

        icon_path = Path(__file__).parent / "assets" / "icon.png"
        self.setIcon(QIcon(str(icon_path)))
        self.setToolTip("Sleepy Rework")

        self.create_menu()

        self.show()

        self.activated.connect(self.on_tray_activated)

    def create_menu(self):
        from qfluentwidgets import FluentIcon, SystemTrayMenu

        self.menu = SystemTrayMenu("Sleepy Rework", parent=self.parent_)
        show_action = Action("显示窗口", self)
        show_action.setIcon(FluentIcon.LINK)
        show_action.triggered.connect(self.show_main_window)

        quit_action = Action("退出应用", self)
        quit_action.setIcon(FluentIcon.CLOSE)
        quit_action.triggered.connect(self.quit_application)

        self.menu.addActions([show_action, quit_action])
        self.setContextMenu(self.menu)

    def show_main_window(self):
        self.parent_.showNormal()
        self.parent_.activateWindow()

    def quit_application(self):
        sys.exit(0)

    def on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_main_window()
