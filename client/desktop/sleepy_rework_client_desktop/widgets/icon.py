from pathlib import Path
from typing import override

from PySide6.QtGui import QColor
from qfluentwidgets import FluentIconBase, Theme, isDarkTheme
from qfluentwidgets.common.icon import ColoredFluentIcon


class LightDarkIcon(FluentIconBase):
    def __init__(self, light: Path | str, dark: Path | str) -> None:
        super().__init__()
        self.light = light
        self.dark = dark

    @override
    def path(self, theme: Theme = Theme.AUTO) -> str:
        return str(self.dark if isDarkTheme() else self.light)


class SvgIcon(FluentIconBase):
    def __init__(self, path: str | Path) -> None:
        super().__init__()
        self._path = path

    def path(self, theme: Theme = Theme.AUTO) -> str:  # noqa: ARG002
        return str(self._path)

    def colored(
        self,
        lightColor: QColor | None = None,
        darkColor: QColor | None = None,
    ) -> ColoredFluentIcon:
        return super().colored(
            lightColor or QColor(0, 0, 0),
            darkColor or QColor(255, 255, 255),
        )
