from abc import abstractmethod
from typing import cast, override

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFocusEvent, QIcon
from PySide6.QtWidgets import QWidget
from qfluentwidgets import (
    ConfigItem,
    FluentIconBase,
    InfoBarIcon,
    LineEdit,
    PasswordLineEdit,
    SettingCard,
    TeachingTip,
    TeachingTipTailPosition,
    qconfig,
)


class AbstractLineEditSettingCard(SettingCard):
    textChanged = Signal(str)

    @abstractmethod
    def makeLineEdit(self) -> LineEdit: ...

    def __init__(
        self,
        icon: str | QIcon | FluentIconBase,
        title: str,
        content: str | None = None,
        configItem: ConfigItem | None = None,
        isReadOnly: bool = False,
        placeHolderText: str = "",
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


class StrictLineEditSettingCard(AbstractLineEditSettingCard):
    class SLineEdit(LineEdit):
        @override
        def focusInEvent(self, e: QFocusEvent | None):
            p = cast("StrictLineEditSettingCard", self.parent())
            if p.lineEdit.isError():
                p.createTip()
            return super().focusInEvent(e)

        @override
        def focusOutEvent(self, e: QFocusEvent | None):
            cast("StrictLineEditSettingCard", self.parent()).closeTip()
            return super().focusOutEvent(e)

    def __init__(
        self,
        icon: str | QIcon | FluentIconBase,
        title: str,
        content: str | None = None,
        configItem: ConfigItem | None = None,
        isReadOnly: bool = False,
        placeHolderText: str = "",
        errorTip: str | None = None,
        parent: QWidget | None = None,
    ):
        self.errorTip = errorTip or ""
        self.tipWidget: TeachingTip | None = None
        super().__init__(
            icon,
            title,
            content,
            configItem,
            isReadOnly,
            placeHolderText,
            parent,
        )

    @override
    def makeLineEdit(self) -> LineEdit:
        return self.SLineEdit(parent=self)

    def createTip(self):
        if self.tipWidget:
            return
        self.tipWidget = TeachingTip.create(
            target=self.lineEdit,
            icon=InfoBarIcon.ERROR,
            title="格式不符合要求",
            content=self.errorTip,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            isClosable=False,
            isDeleteOnClose=False,
            duration=-1,
            parent=self,
        )

    def closeTip(self):
        if not self.tipWidget:
            return
        self.tipWidget.close()
        self.tipWidget.deleteLater()
        self.tipWidget = None

    @override
    def _onTextChanged(self, text: str):
        if self.configItem and (not self.configItem.validator.validate(text)):
            self.lineEdit.setError(True)
            self.createTip()
        else:
            self.lineEdit.setError(False)
            self.closeTip()
            super()._onTextChanged(text)


class PasswordLineEditSettingCard(AbstractLineEditSettingCard):
    @override
    def makeLineEdit(self) -> LineEdit:
        return PasswordLineEdit(parent=self)
