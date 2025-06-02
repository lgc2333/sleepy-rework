from typing import ClassVar

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import InfoBar, InfoBarPosition, PrimaryPushButton


class HomePage(QWidget):
    routeKey: ClassVar[str] = "home"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.setObjectName(self.routeKey)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.setSpacing(20)

        self.button = PrimaryPushButton("点击我", self)
        self.button.setFixedWidth(200)
        self.button.clicked.connect(self.onButtonClicked)
        self.mainLayout.addWidget(self.button)

    def onButtonClicked(self) -> None:
        InfoBar.success(
            title="成功",
            content="您点击了按钮！",
            duration=3000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self,
        )
