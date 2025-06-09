import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from .consts import APP_ID
from .utils.single_app import QtSingleApplication

QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough,
)
QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

app = QtSingleApplication(APP_ID, sys.argv)


def launch():
    if app.isRunning():
        print("Another instance is already running.")
        app.sendMessage("114514")
        sys.exit(0)

    import asyncio
    import traceback

    import qasync
    from PySide6.QtCore import QLocale
    from qfluentwidgets import FluentTranslator, qconfig

    from .config import config
    from .utils.common import AUTO_START_OPT
    from .window import MainWindow

    app.setQuitOnLastWindowClosed(False)

    translator = FluentTranslator(
        QLocale(QLocale.Language.Chinese, QLocale.Country.China),
    )
    app.installTranslator(translator)

    event_loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(event_loop)

    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)

    async def _async_setup(app: QtSingleApplication):
        show = not (
            (AUTO_START_OPT in sys.argv) and qconfig.get(config.appStartMinimized)
        )
        window = MainWindow()
        app.setActivationWindow(window)
        if show:
            window.show()
        window.setup()

    def async_setup_callback(task: asyncio.Task):
        if e := task.exception():
            traceback.print_exception(e)
            app_close_event.set()

    with event_loop:
        event_loop.create_task(
            _async_setup(app),
        ).add_done_callback(async_setup_callback)
        event_loop.run_until_complete(app_close_event.wait())
