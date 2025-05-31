# ruff: noqa: N802, N803, N815

from typing import override

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLineEdit, QWidget
from qfluentwidgets import ConfigItem, FluentIconBase, LineEdit, SettingCard, qconfig


class LineEditSettingCard(SettingCard):
    text_changed = pyqtSignal(str)

    def __init__(
        self,
        icon: str | QIcon | FluentIconBase,
        title: str,
        content: str | None = None,
        configItem: ConfigItem | None = None,
        parent: QWidget | None = None,
        isReadOnly: bool = False,
        placeHolderText: str | None = None,
        echoMode: QLineEdit.EchoMode = QLineEdit.EchoMode.Normal,
    ):
        super().__init__(icon, title, content, parent)
        self.configItem = configItem

        self.lineEdit = LineEdit(self)
        self.lineEdit.setMinimumWidth(200)
        self.lineEdit.setReadOnly(isReadOnly)
        self.lineEdit.setPlaceholderText(placeHolderText)
        self.lineEdit.setEchoMode(echoMode)

        if configItem:
            self.setValue(qconfig.get(configItem))
            configItem.valueChanged.connect(self.setValue)

        self.lineEdit.textChanged.connect(self.__on_text_changed)

        self.hBoxLayout.addWidget(self.lineEdit, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def __on_text_changed(self, text: str):
        if self.configItem:
            qconfig.set(self.configItem, text)
        self.text_changed.emit(text)

    @override
    def setValue(self, value: str):
        self.lineEdit.setText(value)
        if self.configItem:
            qconfig.set(self.configItem, value)

    def text(self) -> str:
        return self.lineEdit.text()
