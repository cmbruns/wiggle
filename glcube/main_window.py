import pkg_resources

from PyQt5 import uic
from PyQt5.Qt import QCoreApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QSettings

import wiggle
import glcube


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self.readSettings()
        self._setup_ui()
        self.camera = wiggle.PerspectiveCamera()
        self.camera.focus = (0, 1.2, 0)
        self.camera.distance = 2
        self.renderer = wiggle.Renderer()
        self._setup_canvas()
        self.multisample_count = self.sampleCountSpinBox.value()
        self.b_multisample = self.multisampleCheckBox.checkState()

    def _setup_ui(self):
        uic.loadUi(uifile=pkg_resources.resource_stream('glcube', 'glcube.ui'), baseinstance=self)
        self.openGLWidget.main_window = self
        self.actionQuit.triggered.connect(self._quit)
        self.actionMultisample.toggled.connect(self.toggle_multisampling)
        self.sampleCountSpinBox.valueChanged.connect(self.set_multisample_count)
        self.actionWireframe.toggled.connect(self.toggle_wireframe)

    def _setup_canvas(self):
        self.openGLWidget.camera = self.camera
        self.openGLWidget.renderer = self.renderer

    def _replace_canvas(self, new_canvas):
        old_canvas = self.openGLWidget
        self.sceneContainer.layout().removeWidget(old_canvas)
        old_canvas.setParent(None)
        self.sceneContainer.layout().addWidget(new_canvas)
        self.openGLWidget = new_canvas
        old_canvas.deleteLater()
        self._setup_canvas()

    def _quit(self):
        # self.closeEvent(None)
        self.saveSettings()
        QCoreApplication.quit()

    def closeEvent(self, event):
        self.saveSettings()
        super().closeEvent(event)

    def readSettings(self):
        settings = QSettings('Brunsgen International', 'glcube')
        self.restoreGeometry(settings.value('geometry'))
        self.restoreState(settings.value('windowState'))
        print('readSettings')

    def saveSettings(self):
        settings = QSettings('Brunsgen International', 'glcube')
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('windowState', self.saveState())
        print('saveSettings')

    def set_multisample_count(self, sample_count):
        self.multisample_count = sample_count
        if self.b_multisample:
            self._change_multisampling(sample_count)

    def _change_multisampling(self, sample_count):
        new_canvas = glcube.scene_canvas.SceneCanvas(self.sceneContainer, samples=sample_count)
        self._replace_canvas(new_canvas)
        QCoreApplication.processEvents()  # required for repaint below to take
        self.openGLWidget.repaint()

    def toggle_multisampling(self, checked):
        self.b_multisample = checked
        if checked:
            self._change_multisampling(self.multisample_count)
        else:
            self._change_multisampling(0)

    def toggle_wireframe(self, checked):
        print('wireframe', checked)
