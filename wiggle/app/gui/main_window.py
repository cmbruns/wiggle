import pkg_resources

from PyQt5 import uic
from PyQt5.Qt import QCoreApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QSettings

import wiggle
from .scene_canvas import SceneCanvas


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self._setup_ui()
        self.camera = wiggle.PerspectiveCamera()
        self.camera.focus = (0, 1.2, 0)
        self.camera.distance = 2
        self.renderer = wiggle.Renderer()
        self._setup_canvas()
        self.multisample_count = self.sampleCountSpinBox.value()
        self.b_multisample = self.multisampleCheckBox.checkState()

    def _change_multisampling(self, sample_count):
        """Creates a new instance of SceneViewer, to support interactive changing of multisampling parameters"""
        new_canvas = SceneCanvas(self.sceneContainer, samples=sample_count)
        old_canvas = self.openGLWidget
        self.sceneContainer.layout().removeWidget(old_canvas)
        old_canvas.setParent(None)
        self.sceneContainer.layout().addWidget(new_canvas)
        self.openGLWidget = new_canvas
        old_canvas.deleteLater()
        self._setup_canvas()
        QCoreApplication.processEvents()  # required for repaint below to take
        self.openGLWidget.repaint()

    def _quit(self):
        self.save_settings()
        QCoreApplication.quit()

    def _setup_ui(self):
        uic.loadUi(uifile=pkg_resources.resource_stream('wiggle.app.gui', 'glcube.ui'), baseinstance=self)
        self.openGLWidget.main_window = self
        self.actionQuit.triggered.connect(self._quit)
        self.actionMultisample.toggled.connect(self.toggle_multisampling)
        self.sampleCountSpinBox.valueChanged.connect(self.set_multisample_count)
        self.actionWireframe.toggled.connect(self.toggle_wireframe)
        self.read_settings()

    def _setup_canvas(self):
        self.openGLWidget.camera = self.camera
        self.openGLWidget.renderer = self.renderer

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

    def read_settings(self):
        settings = QSettings('Brunsgen International', 'glcube')
        self.restoreGeometry(settings.value('geometry'))
        self.restoreState(settings.value('windowState'))

    def save_settings(self):
        settings = QSettings('Brunsgen International', 'glcube')
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('windowState', self.saveState())

    def set_multisample_count(self, sample_count):
        self.multisample_count = sample_count
        if self.b_multisample:
            self._change_multisampling(sample_count)

    def toggle_multisampling(self, checked):
        self.b_multisample = checked
        if checked:
            self._change_multisampling(self.multisample_count)
        else:
            self._change_multisampling(0)

    def toggle_wireframe(self, checked):
        print('wireframe', checked)
