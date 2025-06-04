from PyQt5.QtCore import Qt, QTextStream, pyqtSignal
from PyQt5.QtNetwork import QLocalServer, QLocalSocket
from PyQt5.QtWidgets import QApplication, QWidget


# https://stackoverflow.com/a/79574637
class QtSingleApplication(QApplication):
    messageReceived = pyqtSignal(str)

    def __init__(self, uid: str, *argv):
        super().__init__(*argv)
        self._uid = uid
        self._activationWindow: QWidget | None = None
        self._activateOnMessage: bool = False

        # Is there another instance running?
        self._outSocket = QLocalSocket()
        self._outSocket.connectToServer(self._uid)
        self._isRunning = self._outSocket.waitForConnected()

        if self._isRunning:
            # Yes, there is.
            self._outStream = QTextStream(self._outSocket)
            self._outStream.setCodec("utf-8")
        else:
            # No, there isn't.
            self._outSocket = None
            self._outStream = None
            self._inSocket = None
            self._inStream = None
            self._server = QLocalServer()
            self._server.listen(self._uid)
            self._server.newConnection.connect(self._onNewConnection)

    def isRunning(self):
        return self._isRunning

    def uid(self):
        return self._uid

    def activationWindow(self):
        return self._activationWindow

    def setActivationWindow(
        self,
        activationWindow: QWidget,
        activateOnMessage: bool = True,
    ):
        self._activationWindow = activationWindow
        self._activateOnMessage = activateOnMessage

    def activateWindow(self):
        if not self._activationWindow:
            return

        self._activationWindow.setWindowState(
            self._activationWindow.windowState() & ~Qt.WindowState.WindowMinimized,  # type: ignore
        )
        self._activationWindow.showNormal()
        self._activationWindow.raise_()
        self._activationWindow.activateWindow()

    def sendMessage(self, msg: str):
        if not self._outStream:
            return False
        self._outStream << msg << "\n"  # pyright: ignore[reportUnusedExpression]
        self._outStream.flush()
        if self._outSocket is not None:
            return self._outSocket.waitForBytesWritten()
        return False

    def _onNewConnection(self):
        if self._inSocket:
            self._inSocket.readyRead.disconnect(self._onReadyRead)
        self._inSocket = self._server.nextPendingConnection()
        if not self._inSocket:
            return
        self._inStream = QTextStream(self._inSocket)
        self._inStream.setCodec("utf-8")
        self._inSocket.readyRead.connect(self._onReadyRead)
        if self._activateOnMessage:
            self.activateWindow()

    def _onReadyRead(self):
        while True:
            if self._inStream is not None:
                msg = self._inStream.readLine()
                if not msg:
                    break
                self.messageReceived.emit(msg)
