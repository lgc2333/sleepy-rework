from abc import abstractmethod
from collections.abc import Sequence
from typing import ClassVar, cast, override

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    ComboBox,
    ConfigItem,
    ExpandGroupSettingCard,
    FluentIcon,
    FluentIconBase,
    IndicatorPosition,
    InfoBar,
    InfoBarPosition,
    LineEdit,
    OptionsConfigItem,
    OptionsSettingCard,
    OptionsValidator,
    PasswordLineEdit,
    SettingCard,
    SettingCardGroup,
    SmoothScrollArea,
    SwitchButton,
    SwitchSettingCard,
    qconfig,
)

from ..config import config
from ..utils.auto_start import AutoStartManager


class AbstractLineEditSettingCard(SettingCard):
    textChanged = pyqtSignal(str)

    @abstractmethod
    def makeLineEdit(self) -> LineEdit: ...

    def __init__(
        self,
        icon: str | QIcon | FluentIconBase,
        title: str,
        content: str | None = None,
        configItem: ConfigItem | None = None,
        isReadOnly: bool = False,
        placeHolderText: str | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(icon, title, content, parent)
        self.configItem = configItem

        self.lineEdit = self.makeLineEdit()
        self.lineEdit.setMinimumWidth(200)
        self.lineEdit.setReadOnly(isReadOnly)
        self.lineEdit.setPlaceholderText(placeHolderText)
        self.lineEdit.textChanged.connect(self._onTextChanged)

        if configItem:
            self.setValue(qconfig.get(configItem))
            configItem.valueChanged.connect(self.setValue)

        self.hBoxLayout.addWidget(self.lineEdit, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def _onTextChanged(self, text: str):
        if self.configItem:
            qconfig.set(self.configItem, text)
        self.textChanged.emit(text)

    @override
    def setValue(self, value: str):
        self.lineEdit.setText(value)
        if self.configItem:
            qconfig.set(self.configItem, value)

    def text(self) -> str:
        return self.lineEdit.text()


class LineEditSettingCard(AbstractLineEditSettingCard):
    @override
    def makeLineEdit(self) -> LineEdit:
        return LineEdit(parent=self)


class PasswordLineEditSettingCard(AbstractLineEditSettingCard):
    @override
    def makeLineEdit(self) -> LineEdit:
        return PasswordLineEdit(parent=self)


class ExpandGroupWidget(QWidget):
    def __init__(self, label: QWidget, widget: QWidget, parent: QWidget | None = None):
        super().__init__(parent=parent)

        self.setObjectName("ExpandGroupWidget")
        self.setFixedHeight(60)

        self.label = label
        self.widget = widget
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
        builtInConfig: OptionsConfigItem,
        builtInLabels: Sequence[str],
        customTitle: str,
        customConfig: ConfigItem,
        content: str | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(icon, title, content or "", parent)

        options = cast("OptionsValidator", builtInConfig.validator).options

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
            widget=self.builtInCombo,
        )
        self.customGroup = ExpandGroupWidget(
            label=BodyLabel(customTitle),
            widget=self.customLineEdit,
        )

        self._onAutoSwitchChanged(qconfig.get(autoConfig))

    def addGroupWidget(self, widget: QWidget):
        super().addGroupWidget(widget)
        widget.show()

    def removeGroupWidget(self, widget: QWidget):
        super().removeGroupWidget(widget)
        widget.hide()

    def _onAutoSwitchChanged(self, checked: bool) -> None:
        qconfig.set(self.autoConfig, checked)
        if checked:
            self.removeGroupWidget(self.enableGroup)
            self.removeGroupWidget(self.isCustomGroup)
            self.removeGroupWidget(self.builtInGroup)
            self.removeGroupWidget(self.customGroup)
        else:
            self.addGroupWidget(self.enableGroup)
            self._onEnableSwitchChanged(qconfig.get(self.enableConfig))

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
            self.removeGroupWidget(self.builtInGroup)
            self.addGroupWidget(self.customGroup)
        else:
            self.addGroupWidget(self.builtInGroup)
            self.removeGroupWidget(self.customGroup)

    @override
    def _adjustViewSize(self):
        h = sum(w.maximumSize().height() + 3 for w in self.widgets) - 3
        self.spaceWidget.setFixedHeight(h)

        if self.isExpand:
            self.setFixedHeight(self.card.height() + h)


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

        self.serverEnableSendStatusCard = SwitchSettingCard(
            icon=FluentIcon.SEND,
            title="启用状态发送",
            content="是否向服务器发送设备状态信息",
            configItem=config.serverEnableSendStatus,
        )
        self.serverSettingGroup.addSettingCard(self.serverEnableSendStatusCard)

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

        self.deviceTypeOverrideCard = OverrideExpandGroupSettingCard(
            icon=FluentIcon.CONNECT,
            title="设备类型",
            content="自定义此设备的显示类型",
            autoTitle="自动检测",
            autoConfig=config.deviceTypeOverrideUseDetect,
            enableTitle="覆盖服务端配置",
            enableConfig=config.deviceTypeOverrideEnable,
            isCustomTitle="自定义输入模式",
            isCustomConfig=config.deviceTypeOverrideUseCustom,
            builtInTitle="选择设备类型",
            builtInConfig=config.deviceTypeOverrideValueBuiltIn,
            builtInLabels=[
                "台式电脑",
                "笔记本电脑",
                "手机",
                "平板电脑",
                "智能手表",
                "未知",
            ],
            customTitle="输入设备类型",
            customConfig=config.deviceTypeOverrideValueCustom,
        )
        self.deviceSettingGroup.addSettingCard(self.deviceTypeOverrideCard)

        self.deviceOSOverrideCard = OverrideExpandGroupSettingCard(
            icon=FluentIcon.TILES,
            title="设备操作系统",
            content="自定义此设备显示的操作系统类型",
            autoTitle="自动检测",
            autoConfig=config.deviceOSOverrideUseDetect,
            enableTitle="覆盖服务端配置",
            enableConfig=config.deviceOSOverrideEnable,
            isCustomTitle="自定义输入模式",
            isCustomConfig=config.deviceOSOverrideUseCustom,
            builtInTitle="选择操作系统",
            builtInConfig=config.deviceOSOverrideValueBuiltIn,
            builtInLabels=["Windows", "macOS", "Linux", "Android", "iOS", "未知"],
            customTitle="输入操作系统名称",
            customConfig=config.deviceOSOverrideValueCustom,
        )
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
