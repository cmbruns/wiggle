import pkg_resources

from PyQt5 import uic
from PyQt5.Qt import QCoreApplication
from PyQt5.QtWidgets import QMainWindow

import wiggle
import glcube


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self._setup_ui()
        self.camera = wiggle.PerspectiveCamera()
        self.renderer = wiggle.Renderer()
        self.load_test_scene()
        self._setup_canvas()

    def _setup_ui(self):
        uic.loadUi(uifile=pkg_resources.resource_stream('glcube', 'glcube.ui'), baseinstance=self)
        self.openGLWidget.main_window = self
        self.actionQuit.triggered.connect(QCoreApplication.quit)
        self.actionMultisample.toggled.connect(self.toggle_multisampling)

    def _setup_canvas(self):
        self.openGLWidget.camera = self.camera
        self.openGLWidget.renderer = self.renderer

    def _replace_canvas(self, new_canvas):
        old_canvas = self.openGLWidget
        old_canvas.makeCurrent()
        if self.renderer is not None:
            self.renderer.dispose_gl()
        old_canvas.doneCurrent()
        self.sceneContainer.layout().removeWidget(old_canvas)
        self.sceneContainer.layout().addWidget(new_canvas)
        self.openGLWidget = new_canvas
        old_canvas.deleteLater()
        self._setup_canvas()

    def load_test_scene(self):
        # self.camera.focus = (0, 1.2, 0)
        self.camera.distance = 2
        cube = wiggle.ColorCubeActor()
        # cube.model_center = (0, 1.2, 0)
        cube.scale = 0.3
        self.renderer.add_actor(cube)

    def toggle_multisampling(self, checked):
        samples = 0
        if checked:
            samples = 4
        new_canvas = glcube.scene_canvas.SceneCanvas(self.sceneContainer, samples=samples)
        self._replace_canvas(new_canvas)
        self.update()
        # TODO: cube is not drawing right away
        print(checked)
