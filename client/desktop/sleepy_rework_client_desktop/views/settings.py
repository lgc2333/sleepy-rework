from typing import ClassVar, cast

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    ComboBox,
    FluentIcon,
    IndicatorPosition,
    InfoBar,
    InfoBarPosition,
    LineEdit,
    OptionsSettingCard,
    OptionsValidator,
    SettingCardGroup,
    SmoothScrollArea,
    SwitchButton,
    SwitchSettingCard,
    qconfig,
)

from ..config import config
from ..utils.auto_start import AutoStartManager
from ..widgets import (
    BugFixedExpandGroupSettingCard,
    ExpandGroupWidget,
    LineEditSettingCard,
    PasswordLineEditSettingCard,
    StrictLineEditSettingCard,
)


class DeviceTypeOverrideGroupSettingCard(BugFixedExpandGroupSettingCard):
    def __init__(
        self,
        parent: QWidget | None = None,
    ):
        super().__init__(
            FluentIcon.CONNECT,
            "设备类型",
            "自定义此设备在前端显示的设备类型",
            parent,
        )

        options = cast(
            "OptionsValidator",
            config.deviceTypeOverrideValueBuiltIn.validator,
        ).options

        self.useDefaultSwitch = SwitchButton(indicatorPos=IndicatorPosition.RIGHT)
        self.useDefaultSwitch.setChecked(
            qconfig.get(config.deviceTypeOverrideUseDefault),
        )
        self.useDefaultSwitch.checkedChanged.connect(self._onUseDefaultSwitchChanged)
        self.useDefaultGroup = ExpandGroupWidget(
            label=BodyLabel("使用默认值（台式电脑）"),
            widget=self.useDefaultSwitch,
        )

        self.enableSwitch = SwitchButton(indicatorPos=IndicatorPosition.RIGHT)
        self.enableSwitch.setChecked(qconfig.get(config.deviceTypeOverrideEnable))
        self.enableSwitch.checkedChanged.connect(self._onEnableSwitchChanged)
        self.enableGroup = ExpandGroupWidget(
            label=BodyLabel("覆盖服务端配置"),
            widget=self.enableSwitch,
        )

        self.useCustomSwitch = SwitchButton(indicatorPos=IndicatorPosition.RIGHT)
        self.useCustomSwitch.setChecked(qconfig.get(config.deviceTypeOverrideUseCustom))
        self.useCustomSwitch.checkedChanged.connect(self._onUseCustomSwitchChanged)
        self.useCustomGroup = ExpandGroupWidget(
            label=BodyLabel("自定义输入模式"),
            widget=self.useCustomSwitch,
        )

        self.builtInCombo = ComboBox()
        self.builtInCombo.addItems(
            ["Windows", "macOS", "Linux", "Android", "iOS", "未知"],
        )
        currBuiltInIndex = options.index(
            qconfig.get(config.deviceTypeOverrideValueBuiltIn),
        )
        if currBuiltInIndex >= 0:
            self.builtInCombo.setCurrentIndex(currBuiltInIndex)
        self.builtInCombo.currentIndexChanged.connect(
            lambda index: qconfig.set(
                config.deviceTypeOverrideValueBuiltIn,
                options[index],
            ),
        )
        self.builtInGroup = ExpandGroupWidget(
            label=BodyLabel("选择设备类型"),
            widget=self.builtInCombo,
        )

        self.customLineEdit = LineEdit()
        self.customLineEdit.setText(qconfig.get(config.deviceTypeOverrideValueCustom))
        self.customLineEdit.textChanged.connect(
            lambda text: qconfig.set(config.deviceTypeOverrideValueCustom, text),
        )
        self.customGroup = ExpandGroupWidget(
            label=BodyLabel("输入设备类型"),
            widget=self.customLineEdit,
        )

        self.addGroupWidget(self.useDefaultGroup)
        self._onUseDefaultSwitchChanged(
            qconfig.get(config.deviceTypeOverrideUseDefault),
        )

    def _onUseDefaultSwitchChanged(self, checked: bool) -> None:
        qconfig.set(config.deviceTypeOverrideUseDefault, checked)
        if checked:
            self.removeGroupWidget(self.enableGroup)
            self.removeGroupWidget(self.useCustomGroup)
            self.removeGroupWidget(self.builtInGroup)
            self.removeGroupWidget(self.customGroup)
        else:
            self.addGroupWidget(self.enableGroup)
            self._onEnableSwitchChanged(qconfig.get(config.deviceTypeOverrideEnable))

    def _onEnableSwitchChanged(self, checked: bool) -> None:
        qconfig.set(config.deviceTypeOverrideEnable, checked)
        if checked:
            self.addGroupWidget(self.useCustomGroup)
            self._onUseCustomSwitchChanged(
                qconfig.get(config.deviceTypeOverrideUseCustom),
            )
        else:
            self.removeGroupWidget(self.useCustomGroup)
            self.removeGroupWidget(self.builtInGroup)
            self.removeGroupWidget(self.customGroup)

    def _onUseCustomSwitchChanged(self, checked: bool) -> None:
        qconfig.set(config.deviceTypeOverrideUseCustom, checked)

        if checked:
            self.removeGroupWidget(self.builtInGroup)
            self.addGroupWidget(self.customGroup)
        else:
            self.addGroupWidget(self.builtInGroup)
            self.removeGroupWidget(self.customGroup)


class DeviceOSOverrideGroupSettingCard(BugFixedExpandGroupSettingCard):
    def __init__(
        self,
        parent: QWidget | None = None,
    ):
        super().__init__(
            FluentIcon.TILES,
            "设备操作系统",
            "自定义此设备在前端显示的操作系统类型",
            parent,
        )

        self.useDefaultSwitch = SwitchButton(indicatorPos=IndicatorPosition.RIGHT)
        self.useDefaultSwitch.setChecked(qconfig.get(config.deviceOSOverrideUseDetect))
        self.useDefaultSwitch.checkedChanged.connect(self._onUseDefaultSwitchChanged)
        self.useDefaultGroup = ExpandGroupWidget(
            label=BodyLabel("使用自动检测结果"),
            widget=self.useDefaultSwitch,
        )

        self.enableSwitch = SwitchButton(indicatorPos=IndicatorPosition.RIGHT)
        self.enableSwitch.setChecked(qconfig.get(config.deviceOSOverrideEnable))
        self.enableSwitch.checkedChanged.connect(self._onEnableSwitchChanged)
        self.enableGroup = ExpandGroupWidget(
            label=BodyLabel("覆盖服务端配置"),
            widget=self.enableSwitch,
        )

        self.customLineEdit = LineEdit()
        self.customLineEdit.setText(qconfig.get(config.deviceOSOverrideValue))
        self.customLineEdit.textChanged.connect(
            lambda text: qconfig.set(config.deviceOSOverrideValue, text),
        )
        self.customGroup = ExpandGroupWidget(
            label=BodyLabel("输入操作系统"),
            widget=self.customLineEdit,
        )

        self.addGroupWidget(self.useDefaultGroup)
        self._onUseDefaultSwitchChanged(qconfig.get(config.deviceOSOverrideUseDetect))

    def _onUseDefaultSwitchChanged(self, checked: bool) -> None:
        qconfig.set(config.deviceOSOverrideUseDetect, checked)
        if checked:
            self.removeGroupWidget(self.enableGroup)
            self.removeGroupWidget(self.customGroup)
        else:
            self.addGroupWidget(self.enableGroup)
            self._onEnableSwitchChanged(qconfig.get(config.deviceOSOverrideEnable))

    def _onEnableSwitchChanged(self, checked: bool) -> None:
        qconfig.set(config.deviceOSOverrideEnable, checked)
        if checked:
            self.addGroupWidget(self.customGroup)
        else:
            self.removeGroupWidget(self.customGroup)


class SettingsPage(QWidget):
    routeKey: ClassVar[str] = "settings"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.setObjectName(self.routeKey)

        self.setupUI()

        config.appAutoStart.valueChanged.connect(self.onAutoStartChanged)

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
        self.serverSettingGroup = SettingCardGroup("服务器设置")

        self.serverEnableConnectCard = SwitchSettingCard(
            icon=FluentIcon.POWER_BUTTON,
            title="启用连接",
            content="是否启用与服务端的连接",
            configItem=config.serverEnableConnect,
        )
        self.serverSettingGroup.addSettingCard(self.serverEnableConnectCard)

        self.serverUrlCard = LineEditSettingCard(
            icon=FluentIcon.LINK,
            title="服务器地址",
            content="设置连接的服务器地址",
            configItem=config.serverUrl,
        )
        self.serverSettingGroup.addSettingCard(self.serverUrlCard)

        self.serverSecretCard = PasswordLineEditSettingCard(
            icon=FluentIcon.CERTIFICATE,
            title="服务器密钥",
            content="设置连接服务器所需的密钥",
            configItem=config.serverSecret,
        )
        self.serverSettingGroup.addSettingCard(self.serverSecretCard)

        self.serverConnectProxyCard = StrictLineEditSettingCard(
            icon=FluentIcon.GLOBE,
            title="连接代理",
            content="设置连接服务器时使用的代理（留空则不使用）",
            configItem=config.serverConnectProxy,
        )
        self.serverSettingGroup.addSettingCard(self.serverConnectProxyCard)

        self.scrollContentLayout.addWidget(self.serverSettingGroup)

    def createAppSettings(self) -> None:
        self.appSettingGroup = SettingCardGroup("应用设置")

        self.appAutoStartCard = SwitchSettingCard(
            icon=FluentIcon.POWER_BUTTON,
            configItem=config.appAutoStart,
            title=f"开机自启动{'' if AutoStartManager else '（暂不支持当前系统）'}",
            content="是否在系统启动时自动启动应用",
        )
        if not AutoStartManager:
            self.appAutoStartCard.switchButton.setEnabled(False)
        self.appSettingGroup.addSettingCard(self.appAutoStartCard)

        self.appStartMinimizedCard = SwitchSettingCard(
            icon=FluentIcon.MINIMIZE,
            title="自启时最小化",
            content="是否在自启时自动最小化到系统托盘",
            configItem=config.appStartMinimized,
        )
        self.appSettingGroup.addSettingCard(self.appStartMinimizedCard)

        self.appThemeCard = OptionsSettingCard(
            config.appThemeMode,
            FluentIcon.BRUSH,
            "应用主题",
            "调整你的应用外观",
            texts=["浅色", "深色", "跟随系统设置"],
        )
        self.appSettingGroup.addSettingCard(self.appThemeCard)

        self.scrollContentLayout.addWidget(self.appSettingGroup)

    def createDeviceSettings(self) -> None:
        self.deviceSettingGroup = SettingCardGroup("设备设置")

        self.deviceKeyCard = LineEditSettingCard(
            icon=FluentIcon.TAG,
            title="设备 ID",
            content="此设备的唯一标识名称",
            configItem=config.deviceKey,
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

        self.deviceTypeOverrideCard = DeviceTypeOverrideGroupSettingCard()
        self.deviceSettingGroup.addSettingCard(self.deviceTypeOverrideCard)

        self.deviceOSOverrideCard = DeviceOSOverrideGroupSettingCard()
        self.deviceSettingGroup.addSettingCard(self.deviceOSOverrideCard)

        self.scrollContentLayout.addWidget(self.deviceSettingGroup)

    def onAutoStartChanged(self, checked: bool) -> None:
        if not AutoStartManager:
            return
        self.appAutoStartCard.switchButton.setEnabled(False)
        res = AutoStartManager.enable() if checked else AutoStartManager.disable()
        if not res:
            self.appAutoStartCard.switchButton.setChecked(not checked)
            InfoBar.error(
                "操作失败",
                "设置开机自启失败",
                duration=3000,
                position=InfoBarPosition.TOP_RIGHT,
                parent=self.appAutoStartCard,
            )
        self.appAutoStartCard.switchButton.setEnabled(True)
