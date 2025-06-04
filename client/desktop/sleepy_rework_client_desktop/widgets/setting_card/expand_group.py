from typing import override

from PyQt5.QtWidgets import QHBoxLayout, QWidget
from qfluentwidgets import ExpandGroupSettingCard


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


class BugFixedExpandGroupSettingCard(ExpandGroupSettingCard):
    @override
    def addGroupWidget(self, widget: QWidget):
        super().addGroupWidget(widget)
        widget.show()

    @override
    def removeGroupWidget(self, widget: QWidget):
        super().removeGroupWidget(widget)
        widget.hide()

    @override
    def _adjustViewSize(self):
        h = sum(w.maximumSize().height() + 3 for w in self.widgets) - 3
        self.spaceWidget.setFixedHeight(h)

        if self.isExpand:
            self.setFixedHeight(self.card.height() + h)
