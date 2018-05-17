import sys

from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

from wiggle.app.gui.main_window import MainWindow
import wiggle.render.demo

# For some reason this block causes python exceptions raised during
# rendering to crash with stack traces like I expect.
_report_exceptions = True
if _report_exceptions:
    _cached_excepthook = sys.excepthook

    def exception_hook(exctype, value, traceback):
        _cached_excepthook(exctype, value, traceback)
        sys.exit(1)
    sys.excepthook = exception_hook


class GlCubeApplication(QApplication):
    def __init__(self, arg_list=[]):
        super().__init__(arg_list)
        self.main_window = MainWindow()
        self.main_window.show()

    def load_test_scene(self):
        if False:
            cube = wiggle.render.demo.color_cube_demo()
        else:
            cube = wiggle.render.demo.wireframe_cube_demo()
        self.main_window.renderer.add_actor(cube)

    def run(self):
        sys.exit(self.exec_())


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = GlCubeApplication(sys.argv)
    app.load_test_scene()
    app.run()
