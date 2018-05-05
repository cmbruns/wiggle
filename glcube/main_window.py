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
        self.multisample_count = self.sampleCountSpinBox.value()
        self.b_multisample = self.multisampleCheckBox.checkState()

    def _setup_ui(self):
        uic.loadUi(uifile=pkg_resources.resource_stream('glcube', 'glcube.ui'), baseinstance=self)
        self.openGLWidget.main_window = self
        self.actionQuit.triggered.connect(QCoreApplication.quit)
        self.actionMultisample.toggled.connect(self.toggle_multisampling)
        self.sampleCountSpinBox.valueChanged.connect(self.set_multisamples)

    def _setup_canvas(self):
        self.openGLWidget.camera = self.camera
        self.openGLWidget.renderer = self.renderer

    def _replace_canvas(self, new_canvas):
        old_canvas = self.openGLWidget
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

    def set_multisamples(self, sample_count):
        self.multisample_count = sample_count
        if self.b_multisample:
            self._change_multisamples(sample_count)

    def _change_multisamples(self, sample_count):
        new_canvas = glcube.scene_canvas.SceneCanvas(self.sceneContainer, samples=sample_count)
        self._replace_canvas(new_canvas)
        QCoreApplication.processEvents()  # required for repaint below to take
        self.openGLWidget.repaint()

    def toggle_multisampling(self, checked):
        self.b_multisample = checked
        if checked:
            self._change_multisamples(self.multisample_count)
        else:
            self._change_multisamples(0)
