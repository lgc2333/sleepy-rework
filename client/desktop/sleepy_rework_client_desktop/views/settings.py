from typing import ClassVar

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QWidget
from qfluentwidgets import (
    FluentIcon,
    SmoothScrollArea,
    SubtitleLabel,
    SwitchSettingCard,
)

from ..components import LineEditSettingCard
from ..config import config


class SettingsPage(QWidget):
    route_key: ClassVar[str] = "settings"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.setObjectName(self.route_key)

        self.init_ui()

    def init_ui(self) -> None:
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.scroll_area = SmoothScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(
            "background-color: transparent; border: none;",
        )

        self.scroll_widget = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_content_layout.setContentsMargins(8, 8, 8, 8)
        self.scroll_content_layout.setSpacing(8)
        self.scroll_content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.scroll_widget)
        self.main_layout.addWidget(self.scroll_area)

        self.create_server_settings()
        self.create_app_settings()
        self.create_device_settings()

    def create_server_settings(self) -> None:
        self.server_title_label = SubtitleLabel("服务器设置", parent=self.scroll_widget)
        self.scroll_content_layout.addWidget(self.server_title_label)

        self.server_url_card = LineEditSettingCard(
            icon=FluentIcon.LINK,
            title="服务器地址",
            content="设置连接的服务器地址",
            configItem=config.server_url,
            parent=self.scroll_widget,
        )
        self.scroll_content_layout.addWidget(self.server_url_card)

        self.server_secret_card = LineEditSettingCard(
            icon=FluentIcon.CERTIFICATE,
            title="服务器密钥",
            content="设置连接服务器所需的密钥",
            configItem=config.server_secret,
            parent=self.scroll_widget,
            echoMode=QLineEdit.EchoMode.Password,
        )
        self.scroll_content_layout.addWidget(self.server_secret_card)

    def create_app_settings(self) -> None:
        self.app_title_label = SubtitleLabel("应用设置", parent=self.scroll_widget)
        self.scroll_content_layout.addWidget(self.app_title_label)

        self.app_enable_send_status_card = SwitchSettingCard(
            icon=FluentIcon.SEND,
            title="启用状态发送",
            content="是否向服务器发送设备状态信息",
            configItem=config.app_enable_send_status,
            parent=self.scroll_widget,
        )
        self.scroll_content_layout.addWidget(self.app_enable_send_status_card)

        self.app_auto_start_card = SwitchSettingCard(
            icon=FluentIcon.POWER_BUTTON,
            title="开机自启动",
            content="是否在系统启动时自动启动应用",
            configItem=config.app_auto_start,
            parent=self.scroll_widget,
        )
        self.scroll_content_layout.addWidget(self.app_auto_start_card)

        self.app_start_minimized_card = SwitchSettingCard(
            icon=FluentIcon.MINIMIZE,
            title="启动时最小化",
            content="是否在启动时自动最小化到系统托盘",
            configItem=config.app_start_minimized,
            parent=self.scroll_widget,
        )
        self.scroll_content_layout.addWidget(self.app_start_minimized_card)

    def create_device_settings(self) -> None:
        self.device_title_label = SubtitleLabel("设备设置", parent=self.scroll_widget)
        self.scroll_content_layout.addWidget(self.device_title_label)

        self.device_key_card = LineEditSettingCard(
            icon=FluentIcon.TAG,
            title="设备 ID",
            content="此设备的唯一标识名称",
            configItem=config.device_key,
            parent=self.scroll_widget,
            isReadOnly=True,
        )
        self.scroll_content_layout.addWidget(self.device_key_card)

        self.device_name_card = LineEditSettingCard(
            icon=FluentIcon.PEOPLE,
            title="设备名称",
            content="设置此设备的显示名称（留空使用服务端配置，如为新设备则必须设置）",
            configItem=config.device_name,
            parent=self.scroll_widget,
        )
        self.scroll_content_layout.addWidget(self.device_name_card)

        self.device_description_card = LineEditSettingCard(
            icon=FluentIcon.EDIT,
            title="设备描述",
            content="设置此设备的详细描述（留空使用服务端配置）",
            configItem=config.device_description,
            parent=self.scroll_widget,
        )
        self.scroll_content_layout.addWidget(self.device_description_card)
