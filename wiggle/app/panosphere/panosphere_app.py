import sys

from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

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
        self.main_window = MainWindow()
        self.main_window.show()

    def run(self):
        sys.exit(self.exec_())


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = PanosphereApplication(sys.argv)
    app.run()
