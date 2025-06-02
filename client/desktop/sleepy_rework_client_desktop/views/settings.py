from collections.abc import Sequence
from typing import ClassVar, cast, override

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    ComboBox,
    ConfigItem,
    ExpandGroupSettingCard,
    FluentIcon,
    IndicatorPosition,
    LineEdit,
    OptionsConfigItem,
    OptionsSettingCard,
    OptionsValidator,
    SettingCardGroup,
    SmoothScrollArea,
    SwitchButton,
    SwitchSettingCard,
    qconfig,
)

from ..components import LineEditSettingCard, PasswordLineEditSettingCard
from ..config import config


class ExpandGroupWidget(QWidget):
    def __init__(self, label: QWidget, widget: QWidget, parent: QWidget | None = None):
        super().__init__(parent=parent)

        self.setObjectName("ExpandGroupWidget")
        self.setFixedHeight(60)

        label.setParent(self)
        widget.setParent(self)

        self.hLayout = QHBoxLayout(self)
        self.hLayout.setContentsMargins(48, 12, 48, 12)

        self.hLayout.addWidget(label)
        self.hLayout.addStretch(1)
        self.hLayout.addWidget(widget)


class OverrideExpandGroupSettingCard(ExpandGroupSettingCard):
    def __init__(
        self,
        icon: str | QIcon | FluentIcon,
        title: str,
        autoTitle: str,
        autoConfig: ConfigItem,
        enableTitle: str,
        enableConfig: ConfigItem,
        isCustomTitle: str,
        isCustomConfig: ConfigItem,
        builtInTitle: str,
        builtInWidget: QWidget,
        customTitle: str,
        customWidget: QWidget,
        content: str | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(icon, title, content or "", parent)

        self.autoConfig = autoConfig
        self.enableConfig = enableConfig
        self.isCustomConfig = isCustomConfig

        self.autoSwitch = SwitchButton(indicatorPos=IndicatorPosition.RIGHT)
        self.autoSwitch.setChecked(qconfig.get(autoConfig))
        self.autoSwitch.checkedChanged.connect(self._onAutoSwitchChanged)

        self.autoGroup = ExpandGroupWidget(
            label=BodyLabel(autoTitle),
            widget=self.autoSwitch,
        )
        self.addGroupWidget(self.autoGroup)

        self.enableSwitch = SwitchButton(indicatorPos=IndicatorPosition.RIGHT)
        self.enableSwitch.setChecked(qconfig.get(enableConfig))
        self.enableSwitch.checkedChanged.connect(self._onEnableSwitchChanged)

        self.isCustomSwitch = SwitchButton(indicatorPos=IndicatorPosition.RIGHT)
        self.isCustomSwitch.setChecked(qconfig.get(isCustomConfig))
        self.isCustomSwitch.checkedChanged.connect(self._onIsCustomSwitchChanged)

        self.enableGroup = ExpandGroupWidget(
            label=BodyLabel(enableTitle),
            widget=self.enableSwitch,
        )
        self.isCustomGroup = ExpandGroupWidget(
            label=BodyLabel(isCustomTitle),
            widget=self.isCustomSwitch,
        )
        self.builtInGroup = ExpandGroupWidget(
            label=BodyLabel(builtInTitle),
            widget=builtInWidget,
        )
        self.customGroup = ExpandGroupWidget(
            label=BodyLabel(customTitle),
            widget=customWidget,
        )

        self._onAutoSwitchChanged(qconfig.get(autoConfig))

    def _onAutoSwitchChanged(self, checked: bool) -> None:
        qconfig.set(self.autoConfig, checked)
        if checked:
            self.addGroupWidget(self.enableGroup)
            self._onEnableSwitchChanged(qconfig.get(self.enableConfig))
        else:
            self.removeGroupWidget(self.enableGroup)
            self.removeGroupWidget(self.isCustomGroup)
            self.removeGroupWidget(self.builtInGroup)
            self.removeGroupWidget(self.customGroup)

    def _onEnableSwitchChanged(self, checked: bool) -> None:
        qconfig.set(self.enableConfig, checked)
        if checked:
            self.addGroupWidget(self.isCustomGroup)
            self._onIsCustomSwitchChanged(qconfig.get(self.isCustomConfig))
        else:
            self.removeGroupWidget(self.isCustomGroup)
            self.removeGroupWidget(self.builtInGroup)
            self.removeGroupWidget(self.customGroup)

    def _onIsCustomSwitchChanged(self, checked: bool) -> None:
        qconfig.set(self.isCustomConfig, checked)
        if checked:
            self.addGroupWidget(self.customGroup)
            self.removeGroupWidget(self.builtInGroup)
        else:
            self.removeGroupWidget(self.customGroup)
            self.addGroupWidget(self.builtInGroup)

    @override
    def _adjustViewSize(self):
        h = self.viewLayout.sizeHint().height()
        self.spaceWidget.setFixedHeight(h)

        if self.isExpand:
            self.setFixedHeight(self.card.height() + h)


class EnumStrOverrideExpandGroupSettingCard(OverrideExpandGroupSettingCard):
    def __init__(
        self,
        icon: str | QIcon | FluentIcon,
        title: str,
        autoTitle: str,
        autoConfig: ConfigItem,
        enableTitle: str,
        enableConfig: ConfigItem,
        isCustomTitle: str,
        isCustomConfig: ConfigItem,
        builtInTitle: str,
        builtInConfig: OptionsConfigItem,
        builtInLabels: Sequence[str],
        customTitle: str,
        customConfig: ConfigItem,
        content: str | None = None,
        parent: QWidget | None = None,
    ):
        options = cast("OptionsValidator", builtInConfig.validator).options

        self.builtInCombo = ComboBox()
        self.builtInCombo.addItems(builtInLabels)
        if (index := options.index(qconfig.get(builtInConfig))) >= 0:
            self.builtInCombo.setCurrentIndex(index)
        self.builtInCombo.currentIndexChanged.connect(
            lambda index: qconfig.set(builtInConfig, options[index]),
        )

        self.customLineEdit = LineEdit()
        self.customLineEdit.setText(qconfig.get(customConfig))
        self.customLineEdit.textChanged.connect(
            lambda text: qconfig.set(customConfig, text),
        )

        super().__init__(
            icon,
            title,
            autoTitle,
            autoConfig,
            enableTitle,
            enableConfig,
            isCustomTitle,
            isCustomConfig,
            builtInTitle,
            self.builtInCombo,
            customTitle,
            self.customLineEdit,
            content,
            parent,
        )


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
            isReadOnly=True,
        )
        self.deviceSettingGroup.addSettingCard(self.deviceKeyCard)

        self.deviceNameCard = LineEditSettingCard(
            icon=FluentIcon.PEOPLE,
            title="设备名称",
            content="设置此设备的显示名称（留空使用服务端配置，如为新设备则必须设置）",
            configItem=config.deviceName,
        )
        self.deviceSettingGroup.addSettingCard(self.deviceNameCard)

        self.deviceDescriptionCard = LineEditSettingCard(
            icon=FluentIcon.EDIT,
            title="设备描述",
            content="设置此设备的详细描述（留空使用服务端配置）",
            configItem=config.deviceDescription,
        )
        self.deviceSettingGroup.addSettingCard(self.deviceDescriptionCard)

        self.deviceTypeOverrideCard = EnumStrOverrideExpandGroupSettingCard(
            icon=FluentIcon.LIBRARY,
            title="设备类型",
            content="自定义此设备的显示类型",
            autoTitle="自动检测并上报",
            autoConfig=config.deviceEnableTypeDetect,
            enableTitle="手动配置而不使用服务端配置",
            enableConfig=config.deviceEnableTypeOverride,
            isCustomTitle="使用自定义类型而不是内置选项",
            isCustomConfig=config.deviceIsCustomTypeOverride,
            builtInTitle="选择设备类型",
            builtInConfig=config.deviceBuiltInTypeOverride,
            builtInLabels=["台式", "笔记本", "手机", "平板", "手表", "其他"],
            customTitle="输入设备类型",
            customConfig=config.deviceCustomTypeOverride,
        )
        self.deviceSettingGroup.addSettingCard(self.deviceTypeOverrideCard)

        self.deviceOSOverrideCard = EnumStrOverrideExpandGroupSettingCard(
            icon=FluentIcon.LIBRARY,
            title="设备操作系统",
            content="自定义此设备显示的操作系统类型",
            autoTitle="自动检测并上报",
            autoConfig=config.deviceEnableOSDetect,
            enableTitle="手动配置而不使用服务端配置",
            enableConfig=config.deviceEnableOSOverride,
            isCustomTitle="使用自定义操作系统而不是内置选项",
            isCustomConfig=config.deviceIsCustomOSOverride,
            builtInTitle="选择操作系统",
            builtInConfig=config.deviceBuiltInOSOverride,
            builtInLabels=["Windows", "macOS", "Linux", "Android", "iOS", "其他"],
            customTitle="输入操作系统名称",
            customConfig=config.deviceCustomOSOverride,
        )
        self.deviceSettingGroup.addSettingCard(self.deviceOSOverrideCard)

        self.scrollContentLayout.addWidget(self.deviceSettingGroup)
