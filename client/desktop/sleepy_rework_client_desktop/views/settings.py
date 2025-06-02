from typing import ClassVar

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import (
    FluentIcon,
    OptionsSettingCard,
    SettingCardGroup,
    SmoothScrollArea,
    SwitchSettingCard,
)

from ..components import LineEditSettingCard, PasswordLineEditSettingCard
from ..config import config


class SettingsPage(QWidget):
    routeKey: ClassVar[str] = "settings"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.setObjectName(self.routeKey)

        self.setupUI()

    def setupUI(self) -> None:
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        self.scrollArea = SmoothScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet(
            "background-color: transparent; border: none;",
        )

        self.scrollWidget = QWidget()
        self.scrollContentLayout = QVBoxLayout(self.scrollWidget)
        self.scrollContentLayout.setContentsMargins(8, 8, 8, 8)
        self.scrollContentLayout.setSpacing(8)
        self.scrollContentLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scrollArea.setWidget(self.scrollWidget)
        self.mainLayout.addWidget(self.scrollArea)

        self.createServerSettings()
        self.createAppSettings()
        self.createDeviceSettings()

    def createServerSettings(self) -> None:
        self.serverSettingGroup = SettingCardGroup(
            "服务器设置",
            parent=self.scrollWidget,
        )

        self.serverEnableSendStatusCard = SwitchSettingCard(
            icon=FluentIcon.SEND,
            title="启用状态发送",
            content="是否向服务器发送设备状态信息",
            configItem=config.serverEnableSendStatus,
            parent=self.scrollWidget,
        )
        self.serverSettingGroup.addSettingCard(self.serverEnableSendStatusCard)

        self.serverUrlCard = LineEditSettingCard(
            icon=FluentIcon.LINK,
            title="服务器地址",
            content="设置连接的服务器地址",
            configItem=config.serverUrl,
            parent=self.scrollWidget,
        )
        self.serverSettingGroup.addSettingCard(self.serverUrlCard)

        self.serverSecretCard = PasswordLineEditSettingCard(
            icon=FluentIcon.CERTIFICATE,
            title="服务器密钥",
            content="设置连接服务器所需的密钥",
            configItem=config.serverSecret,
            parent=self.scrollWidget,
        )
        self.serverSettingGroup.addSettingCard(self.serverSecretCard)

        self.scrollContentLayout.addWidget(self.serverSettingGroup)

    def createAppSettings(self) -> None:
        self.appSettingGroup = SettingCardGroup(
            "应用设置",
            parent=self.scrollWidget,
        )

        self.appAutoStartCard = SwitchSettingCard(
            icon=FluentIcon.POWER_BUTTON,
            title="开机自启动",
            content="是否在系统启动时自动启动应用",
            configItem=config.appAutoStart,
            parent=self.scrollWidget,
        )
        self.appSettingGroup.addSettingCard(self.appAutoStartCard)

        self.appStartMinimizedCard = SwitchSettingCard(
            icon=FluentIcon.MINIMIZE,
            title="启动时最小化",
            content="是否在启动时自动最小化到系统托盘",
            configItem=config.appStartMinimized,
            parent=self.scrollWidget,
        )
        self.appSettingGroup.addSettingCard(self.appStartMinimizedCard)

        self.appThemeCard = OptionsSettingCard(
            config.appThemeMode,
            FluentIcon.BRUSH,
            "应用主题",
            "调整你的应用外观",
            texts=["浅色", "深色", "跟随系统设置"],
            parent=self.scrollWidget,
        )
        self.appSettingGroup.addSettingCard(self.appThemeCard)

        self.scrollContentLayout.addWidget(self.appSettingGroup)

    def createDeviceSettings(self) -> None:
        self.deviceSettingGroup = SettingCardGroup(
            "设备设置",
            parent=self.scrollWidget,
        )

        self.deviceKeyCard = LineEditSettingCard(
            icon=FluentIcon.TAG,
            title="设备 ID",
            content="此设备的唯一标识名称",
            configItem=config.deviceKey,
            parent=self.scrollWidget,
            isReadOnly=True,
        )
        self.deviceSettingGroup.addSettingCard(self.deviceKeyCard)

        self.deviceNameCard = LineEditSettingCard(
            icon=FluentIcon.PEOPLE,
            title="设备名称",
            content="设置此设备的显示名称（留空使用服务端配置，如为新设备则必须设置）",
            configItem=config.deviceName,
            parent=self.scrollWidget,
        )
        self.deviceSettingGroup.addSettingCard(self.deviceNameCard)

        self.deviceDescriptionCard = LineEditSettingCard(
            icon=FluentIcon.EDIT,
            title="设备描述",
            content="设置此设备的详细描述（留空使用服务端配置）",
            configItem=config.deviceDescription,
            parent=self.scrollWidget,
        )
        self.deviceSettingGroup.addSettingCard(self.deviceDescriptionCard)

        self.scrollContentLayout.addWidget(self.deviceSettingGroup)
