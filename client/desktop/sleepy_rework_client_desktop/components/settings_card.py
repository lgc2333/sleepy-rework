from abc import abstractmethod
from typing import override

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import (
    ConfigItem,
    FluentIconBase,
    LineEdit,
    PasswordLineEdit,
    SettingCard,
    qconfig,
)


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
        parent: QWidget | None = None,
        isReadOnly: bool = False,
        placeHolderText: str | None = None,
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
