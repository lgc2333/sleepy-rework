from typing import ClassVar, override

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    FluentIcon,
    HeaderCardWidget,
    IconWidget,
    InfoBarIcon,
    TitleLabel,
    ToolButton,
)

from ..utils.client.info import info_feeder
from ..utils.common import get_str_time, wrap_async
from ..widgets.scroll_area import VerticalScrollAreaView


class HeaderWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.vLayout = QVBoxLayout(self)
        self.vLayout.setContentsMargins(8, 8, 8, 8)
        self.setLayout(self.vLayout)

        self.welcomeTitle = TitleLabel("欢迎使用 Sleepy Rework 客户端")
        self.welcomeTip = BodyLabel(
            "在所有事情配置完毕后，您可以放心地关闭本窗口，本软件将会常驻后台运行。"
            "\n您可以在系统托盘中找到本软件的图标"
            "，双击图标可以打开本窗口，右键图标打开菜单则可以完全关闭本软件。",
        )
        self.vLayout.addWidget(self.welcomeTitle)
        self.vLayout.addWidget(self.welcomeTip)


class ConnectionStatusCard(HeaderCardWidget):
    def __init__(self, parent: QWidget | None = None):  # type: ignore
        super().__init__(parent)
        self.setTitle("连接状态")

        self.vLayout = QVBoxLayout(self)
        self.viewLayout.addLayout(self.vLayout)

        self.statusLayout = QHBoxLayout()
        self.vLayout.addLayout(self.statusLayout)
        self.statusLayout.setSpacing(8)
        self.statusIcon = IconWidget()
        self.statusIcon.setFixedSize(16, 16)
        self.statusText = BodyLabel()
        self.statusLayout.addWidget(self.statusIcon)
        self.statusLayout.addWidget(self.statusText)

        self.descText = BodyLabel()
        self.descText.hide()
        self.vLayout.addWidget(self.descText)

        self.isDisconnect = False

        self.onBackgroundStopped()

        info_feeder.on_background_started.connect(
            lambda _: wrap_async(self.onBackgroundStarted),
        )
        info_feeder.on_background_stopped.connect(
            lambda _: wrap_async(self.onBackgroundStopped),
        )
        info_feeder.on_connect_error.connect(
            lambda _, e: wrap_async(self.onError, e),
        )
        info_feeder.on_connected.connect(
            lambda _: wrap_async(self.onConnected),
        )
        info_feeder.on_disconnected.connect(
            lambda _, e: wrap_async(self.onDisconnected, e),
        )

    def onBackgroundStarted(self):
        self.isDisconnect = False
        self.statusIcon.setIcon(InfoBarIcon.INFORMATION)
        self.statusText.setText("正尝试与服务端建立连接")
        self.descText.hide()

    def onBackgroundStopped(self):
        self.isDisconnect = False
        self.statusIcon.setIcon(InfoBarIcon.INFORMATION)
        self.statusText.setText("还未与服务端建立连接")
        self.descText.setText(
            "如果您是第一次使用，请前往设置页面修改配置后，启用服务端连接。",
        )
        self.descText.show()

    def onError(self, e: Exception):
        if not self.isDisconnect:
            self.statusIcon.setIcon(InfoBarIcon.WARNING)
            self.statusText.setText(
                f"于 {get_str_time()} 尝试连接服务端失败，正在重连中",
            )
        self.descText.setText(str(e))
        self.descText.show()

    def onConnected(self):
        self.statusIcon.setIcon(InfoBarIcon.SUCCESS)
        self.statusText.setText(f"已于 {get_str_time()} 成功连接到服务端")
        self.descText.hide()

    def onDisconnected(self, e: Exception):
        self.isDisconnect = True
        self.statusIcon.setIcon(InfoBarIcon.WARNING)
        self.statusText.setText(
            f"于 {get_str_time()} 因意外断开了与服务端的连接，正在重连中",
        )
        self.descText.setText(str(e))
        self.descText.show()


class MonoBodyLabel(BodyLabel):
    @override
    def getFont(self):
        f = QFont(
            [
                "JetBrains Mono",
                "Cascadia Code",
                "Ubuntu Mono",
                "Consolas",
                "Courier New",
                "Segoe UI",
                "Microsoft YaHei",
                "PingFang SC",
            ],
            weight=QFont.Weight.Normal,
        )
        f.setStyleHint(QFont.StyleHint.Monospace)
        f.setPixelSize(14)
        return f


class CodeCard(HeaderCardWidget):
    def __init__(self, parent: QWidget | None = None):  # type: ignore
        super().__init__(parent)

        self.headerLayout.addStretch(1)

        self.copyButton = ToolButton(FluentIcon.COPY)
        self.copyButton.clicked.connect(self._onCopyClicked)
        self.headerLayout.addWidget(self.copyButton)

        self.copyIconResetTimer: QTimer | None = None

        self.bodyLabel = MonoBodyLabel()
        self.viewLayout.addWidget(self.bodyLabel)

    def _onCopyClicked(self):
        from ..app import app

        app.clipboard().setText(self.bodyLabel.text())
        self.copyButton.setIcon(FluentIcon.ACCEPT)
        if self.copyIconResetTimer:
            self.copyIconResetTimer.stop()
        self.copyIconResetTimer = QTimer(self)
        self.copyIconResetTimer.singleShot(
            3000,
            lambda: self.copyButton.setIcon(FluentIcon.COPY),
        )


class CurrentClientSideInfoCard(CodeCard):
    def __init__(self, parent: QWidget | None = None):  # type: ignore
        super().__init__(parent)
        self.setTitle("客户端侧当前信息")

        info_feeder.on_info_update.connect(lambda *_: wrap_async(self._onInfoUpdate))
        self._onInfoUpdate()

    def _onInfoUpdate(self):
        self.bodyLabel.setText(
            info_feeder.initial_info.model_dump_json(indent=2, exclude_unset=True),
        )


class CurrentServerSideInfoCard(CodeCard):
    def __init__(self, parent: QWidget | None = None):  # type: ignore
        super().__init__(parent)
        self.setTitle("服务端侧当前信息")

        info_feeder.on_server_side_info_updated.connect(
            lambda *_: wrap_async(self._onInfoUpdate),
        )
        self._onInfoUpdate()

    def _onInfoUpdate(self):
        if (not info_feeder.server_side_info) or (not info_feeder.connected):
            self.bodyLabel.setText("null")
        else:
            self.bodyLabel.setText(
                info_feeder.server_side_info.model_dump_json(indent=2),
            )


class HomePage(VerticalScrollAreaView):
    routeKey: ClassVar[str] = "home"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.setObjectName(self.routeKey)

    def setupContent(self):
        self.headerWidget = HeaderWidget()
        self.addWidget(self.headerWidget)

        self.connectionStatusCard = ConnectionStatusCard()
        self.addWidget(self.connectionStatusCard)

        self.currentClientSideInfoCard = CurrentClientSideInfoCard()
        self.addWidget(self.currentClientSideInfoCard)

        self.currentServerSideInfoCard = CurrentServerSideInfoCard()
        self.addWidget(self.currentServerSideInfoCard)
