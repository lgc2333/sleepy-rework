from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import SingleDirectionScrollArea


class VerticalScrollAreaView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        self.scrollArea = SingleDirectionScrollArea(orient=Qt.Orientation.Vertical)
        self.scrollArea.setWidgetResizable(True)

        self.scrollWidget = QWidget()
        self.scrollContentLayout = QVBoxLayout(self.scrollWidget)
        self.scrollContentLayout.setContentsMargins(8, 8, 8, 8)
        self.scrollContentLayout.setSpacing(8)
        self.scrollArea.setWidget(self.scrollWidget)

        self.scrollArea.enableTransparentBackground()
        self.mainLayout.addWidget(self.scrollArea)

        self.setupContent()

        self.scrollContentLayout.addStretch()

    def setupContent(self):
        pass

    def addWidget(self, widget: QWidget):
        self.scrollContentLayout.addWidget(widget)
