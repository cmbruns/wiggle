import pkg_resources

from PyQt5 import uic
from PyQt5.Qt import QCoreApplication
from PyQt5.QtWidgets import QMainWindow

import wiggle


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self.ui = uic.loadUi(uifile=pkg_resources.resource_stream('glcube', 'glcube.ui'), baseinstance=self)
        self.ui.actionQuit.triggered.connect(QCoreApplication.quit)
        self.openGLWidget.main_window = self
        self.camera = wiggle.PerspectiveCamera()
        self.openGLWidget.camera = self.camera
        self.renderer = wiggle.Renderer()
        self.openGLWidget.renderer = self.renderer
        #
        self.load_test_scene()

    def load_test_scene(self):
        self.camera.focus = (0, 1.2, 0)
        self.camera.distance = 5
        cube = wiggle.ColorCubeActor()
        cube.model_center = (0, 1.2, 0)
        cube.scale = 0.3
        self.renderer.add_actor(cube)
