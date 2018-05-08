import sys

from PyQt5 import QtCore

from wiggle.app.gui.glcube_app import GlCubeApplication


def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = GlCubeApplication(sys.argv)
    app.load_test_scene()
    app.run()


if __name__ == '__main__':
    main()
