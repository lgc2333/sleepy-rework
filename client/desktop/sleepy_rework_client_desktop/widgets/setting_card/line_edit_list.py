from functools import partial

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QWidget
from qfluentwidgets import (
    ConfigItem,
    ExpandSettingCard,
    FluentIcon,
    LineEdit,
    PushButton,
    ToolButton,
    qconfig,
)


class LineEditListLine(QWidget):
    contentChanged = Signal(str)
    removeClicked = Signal()

    def __init__(
        self,
        content: str | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.hLayout = QHBoxLayout(self)
        self.hLayout.setContentsMargins(16, 8, 16, 8)
        self.setLayout(self.hLayout)

        self.lineEdit = LineEdit()
        if content:
            self.lineEdit.setText(content)
        self.lineEdit.textChanged.connect(self.contentChanged.emit)
        self.hLayout.addWidget(self.lineEdit, stretch=1)

        self.removeButton = ToolButton(FluentIcon.DELETE)
        self.removeButton.setFixedSize(33, 33)
        self.removeButton.clicked.connect(self.removeClicked.emit)
        self.hLayout.addWidget(self.removeButton)


class LineEditListSettingCard(ExpandSettingCard):
    valueChanged = Signal(object)

    def __init__(
        self,
        configItem: ConfigItem,
        icon: str | QIcon | FluentIcon,
        title: str,
        content: str = "",
        addButtonTitle: str | None = None,
        addButtonIcon: str | QIcon | FluentIcon | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(icon, title, content, parent)

        self.configItem = configItem
        self.configItem.valueChanged.connect(self._onConfigItemValueChanged)

        self.configRaw: list[str] = []
        self.listWidgets: list[LineEditListLine] = []

        self.addButtonTitle = addButtonTitle or "添加项目"
        self.addButtonIcon = addButtonIcon or FluentIcon.ADD

        self.addButton = PushButton(self.addButtonTitle, icon=self.addButtonIcon)
        self.addButton.clicked.connect(self._onAddButtonClicked)
        self.addWidget(self.addButton)

        self.viewLayout.setSpacing(0)
        self.viewLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.viewLayout.setContentsMargins(0, 8, 0, 8)

        self.setExpand(True)

        self._initList()

    def _addItem(self, initialValue: str = ""):
        self.configRaw.append(initialValue)
        lineEdit = LineEditListLine(initialValue)
        lineEdit.contentChanged.connect(partial(self._onItemValueChange, lineEdit))
        lineEdit.removeClicked.connect(partial(self._onItemDeletePushed, lineEdit))
        self.viewLayout.addWidget(lineEdit)
        self.listWidgets.append(lineEdit)
        QTimer.singleShot(0, self._adjustViewSize)

    def _initList(self):
        for widget in self.listWidgets:
            widget.hide()
            widget.deleteLater()
        self.listWidgets.clear()

        v: list[str] = qconfig.get(self.configItem)
        for it in v:
            self._addItem(it)

    def _onConfigItemValueChanged(self, value: list[str]):
        if self.configRaw == value:
            return
        self.configRaw = value
        self._initList()

    def _dispatchSelfValueChange(self):
        qconfig.set(self.configItem, self.configRaw)
        self.valueChanged.emit(self.configRaw)

    def _onAddButtonClicked(self):
        self._addItem()
        self._dispatchSelfValueChange()

    def _onItemValueChange(self, item: LineEditListLine, value: str):
        index = self.listWidgets.index(item)
        if index == -1:
            raise ValueError("Item not found in listWidgets")
        self.configRaw[index] = value
        self._dispatchSelfValueChange()

    def _onItemDeletePushed(self, item: LineEditListLine):
        index = self.listWidgets.index(item)
        if index == -1:
            raise ValueError("Item not found in listWidgets")
        self.listWidgets.remove(item)
        item.hide()
        item.deleteLater()
        del self.configRaw[index]
        self._dispatchSelfValueChange()
        QTimer.singleShot(0, self._adjustViewSize)
