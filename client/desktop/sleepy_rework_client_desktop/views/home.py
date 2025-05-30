from typing import ClassVar

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import InfoBar, InfoBarPosition, PrimaryPushButton


class HomePage(QWidget):
    route_key: ClassVar[str] = "home"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.setObjectName(self.route_key)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setSpacing(20)

        self.button = PrimaryPushButton("点击我", self)
        self.button.setFixedWidth(200)
        self.button.clicked.connect(self.on_button_clicked)
        self.main_layout.addWidget(self.button)

    def on_button_clicked(self) -> None:
        InfoBar.success(
            title="成功",
            content="您点击了按钮！",
            duration=3000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self,
        )
