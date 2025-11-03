from typing import ClassVar, override

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QMouseEvent, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import BodyLabel, PushButton, SubtitleLabel

from ..assets import ICON_PATH, PROICONS_GITHUB_BLACK_PATH, PROICONS_GITHUB_WHITE_PATH
from ..consts import APP_NAME, GITHUB_LINK
from ..widgets import LightDarkIcon


class EasterTipLabel(BodyLabel):
    def __init__(self, parent: QWidget | None = None) -> None:  # pyright: ignore[reportIncompatibleVariableOverride]
        super().__init__(parent)
        self.texts = ["按下神秘按键序列有彩蛋哦～(∠・ω<)⌒★", "请看我…我我我……（脸红）"]
        self.currTextIndex = 0
        self.setText(self.texts[self.currTextIndex])

    def changeText(self):
        self.currTextIndex = (self.currTextIndex + 1) % len(self.texts)
        self.setText(self.texts[self.currTextIndex])

    @override
    def mouseReleaseEvent(self, ev: QMouseEvent, /) -> None:
        if ev.button() == Qt.MouseButton.LeftButton:
            self.changeText()
        super().mouseReleaseEvent(ev)


class AboutPage(QWidget):
    routeKey: ClassVar[str] = "about"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName(self.routeKey)
        self.setupContent()

    def setupContent(self):
        from .. import __version__
        from .._build_conf import commit_hash

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # App Icon
        appIconLabel = QLabel()
        appIconLabel.setPixmap(
            QPixmap(ICON_PATH).scaled(
                128,
                128,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ),
        )
        appIconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(appIconLabel)

        # App Name
        nameLabel = SubtitleLabel(APP_NAME)
        nameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(nameLabel)

        versionText = f"v{__version__} (git-{commit_hash})"
        versionLabel = BodyLabel(versionText)
        versionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(versionLabel)

        # Author
        authorLabel = BodyLabel("Made with ❤️ by LgCookie")
        authorLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(authorLabel)

        easterTipLabel = EasterTipLabel()
        easterTipLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(easterTipLabel)

        # Links
        linksLayout = QHBoxLayout()
        linksLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        linksLayout.setContentsMargins(0, 10, 0, 0)

        githubButton = PushButton(
            LightDarkIcon(PROICONS_GITHUB_BLACK_PATH, PROICONS_GITHUB_WHITE_PATH),
            "GitHub",
        )
        githubButton.setCursor(Qt.CursorShape.PointingHandCursor)
        githubButton.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(GITHUB_LINK)),
        )
        linksLayout.addWidget(githubButton)

        layout.addLayout(linksLayout)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
