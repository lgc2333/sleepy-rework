from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon, QWidget
from qfluentwidgets import Action

from .consts import APP_NAME


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent: QWidget, icon: QIcon):
        super().__init__(parent)
        self.parent_ = parent

        self.setIcon(icon)
        self.setToolTip(APP_NAME)

        self.createMenu()
        self.activated.connect(self._onTrayActivated)

        self.show()

    def createMenu(self):
        from qfluentwidgets import FluentIcon, SystemTrayMenu

        self.menu = SystemTrayMenu(APP_NAME, parent=self.parent_)
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
        from .app import app

        app.quit()

    def _onTrayActivated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_main_window()
