import traceback
from collections.abc import Callable
from pathlib import Path
from typing import Any, override

from PySide6.QtCore import QEvent, QObject, Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QKeyEvent
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from qfluentwidgets import InfoBar, InfoBarPosition

from ..assets import CIALLO_PATH, SEE_MINE_0721_PATH


class EasterEventFilter(QObject):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.easterKeyStrokes: tuple[
            tuple[
                tuple[Qt.Key, ...],
                Callable[[], Any],
            ],
            ...,
        ] = (
            (
                (Qt.Key.Key_0, Qt.Key.Key_D, Qt.Key.Key_0, Qt.Key.Key_0),
                self.ayachiNeneEaster,
            ),
            (
                (Qt.Key.Key_0, Qt.Key.Key_7, Qt.Key.Key_2, Qt.Key.Key_1),
                self.ayachiNeneEaster,
            ),
            (
                (
                    Qt.Key.Key_C,
                    Qt.Key.Key_I,
                    Qt.Key.Key_A,
                    Qt.Key.Key_L,
                    Qt.Key.Key_L,
                    Qt.Key.Key_O,
                ),
                self.inabaMeguruEaster,
            ),
            (
                (
                    Qt.Key.Key_Up,
                    Qt.Key.Key_Up,
                    Qt.Key.Key_Down,
                    Qt.Key.Key_Down,
                    Qt.Key.Key_Left,
                    Qt.Key.Key_Right,
                    Qt.Key.Key_Left,
                    Qt.Key.Key_Right,
                    Qt.Key.Key_B,
                    Qt.Key.Key_A,
                ),
                self.konamiCodeEaster,
            ),
        )
        self.currentStrokes: list[Qt.Key] = []

        self.audioOutput: QAudioOutput | None = None
        self.mediaPlayer: QMediaPlayer | None = None
        self.disposeWaitTimer: QTimer | None = None
        self.currentPlaying: bool = False

    def _onDisposeTimerTrigger(self):
        # print("dispose timer triggered")
        # maybe the timer is not cancelled properly, double check the player is stopped
        # idk why
        if self.currentPlaying:
            return
        self.disposePlayer()
        if self.disposeWaitTimer:
            self.disposeWaitTimer.deleteLater()
            self.disposeWaitTimer = None

    def _onPlayingChanged(self, playing: bool):
        # print("playing changed:", playing)
        self.currentPlaying = playing
        if playing:
            if self.disposeWaitTimer:
                self.disposeWaitTimer.stop()
                self.disposeWaitTimer.deleteLater()
                self.disposeWaitTimer = None
        else:
            self.disposeWaitTimer = QTimer()
            self.disposeWaitTimer.singleShot(500, self._onDisposeTimerTrigger)

    def getMediaPlayer(self, path: Path | str):
        if not self.audioOutput:
            self.audioOutput = QAudioOutput()
            self.audioOutput.setVolume(0.5)

        if not self.mediaPlayer:
            self.mediaPlayer = QMediaPlayer()
            self.mediaPlayer.setAudioOutput(self.audioOutput)
            self.mediaPlayer.playingChanged.connect(self._onPlayingChanged)
        else:
            self.mediaPlayer.stop()
        self.mediaPlayer.setSource(QUrl.fromLocalFile(path))

        return self.mediaPlayer

    def disposePlayer(self):
        # print("player dispose")
        if self.mediaPlayer:
            self.mediaPlayer.stop()
            self.mediaPlayer.deleteLater()
            self.mediaPlayer = None
        if self.audioOutput:
            self.audioOutput.deleteLater()
            self.audioOutput = None

    def playSound(self, path: Path | str):
        try:
            self.getMediaPlayer(path).play()
        except Exception:
            traceback.print_exc()

    def ayachiNeneEaster(self):
        self.playSound(SEE_MINE_0721_PATH)
        QDesktopServices.openUrl(QUrl("https://0d00.cn"))

    def inabaMeguruEaster(self):
        self.playSound(CIALLO_PATH)
        QDesktopServices.openUrl(QUrl("https://ciallo.cc"))

    def konamiCodeEaster(self):
        InfoBar.info(
            "很可惜，这里什么都没有（悲）",
            (
                "其实没想好应该在这个按键序列彩蛋里塞什么东西（\n"
                "或许可以试试其他序列喵～(∠・ω<)⌒★"
            ),
            orient=Qt.Orientation.Vertical,
            duration=8000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self.parent(),
        )

    def keyPressHandler(self, event: QKeyEvent):
        self.currentStrokes.append(Qt.Key(event.key()))

        while self.currentStrokes:
            is_prefix = False
            for keys, _ in self.easterKeyStrokes:
                if keys[: len(self.currentStrokes)] == tuple(self.currentStrokes):
                    is_prefix = True
                    break
            if is_prefix:
                break
            self.currentStrokes.pop(0)

        if not self.currentStrokes:
            return

        curr_strokes_len = len(self.currentStrokes)
        for keys, action in self.easterKeyStrokes:
            if curr_strokes_len == len(keys) and tuple(self.currentStrokes) == keys:
                action()
                self.currentStrokes.clear()
                return

    @override
    def eventFilter(self, watched: QObject, event: QEvent):
        super().eventFilter(watched, event)
        if event.type() == QEvent.Type.KeyPress:
            assert isinstance(event, QKeyEvent)
            self.keyPressHandler(event)
        return False
