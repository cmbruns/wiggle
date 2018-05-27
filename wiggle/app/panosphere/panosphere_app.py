import ctypes
import pkg_resources
import sys

from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

from wiggle.app.panosphere.main_window import MainWindow


# For some reason this block causes python exceptions raised during
# rendering to crash with stack traces like I expect.
_report_exceptions = True
if _report_exceptions:
    _cached_excepthook = sys.excepthook

    def exception_hook(exctype, value, traceback):
        _cached_excepthook(exctype, value, traceback)
        sys.exit(1)
    sys.excepthook = exception_hook


class PanosphereApplication(QApplication):
    def __init__(self, arg_list=[]):
        super().__init__(arg_list)
        # https://stackoverflow.com/a/1552105/146574
        myappid = u'brunsgen.panosphere.0.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        # https://stackoverflow.com/a/21330349/146574 but it did not work for me
        app_icon = QIcon()
        for s in (16, 24, 32, 48, 64, 128, 256):
            icon_file = pkg_resources.resource_filename(
                'wiggle.app.panosphere.images',
                f'PanosphereIcon{s}.png')
            app_icon.addFile(icon_file, QSize(s, s))
        self.setWindowIcon(app_icon)
        self.main_window = MainWindow()
        self.main_window.show()

    def run(self):
        sys.exit(self.exec_())


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = PanosphereApplication(sys.argv)
    app.run()
