import pkg_resources

from PyQt5 import uic
from PyQt5.Qt import QCoreApplication, QModelIndex
from PyQt5.QtWidgets import QMainWindow, QPushButton
from PyQt5.QtCore import QSettings

from wiggle.geometry.camera import PerspectiveCamera
from wiggle.render.renderer import Renderer
from .scene_canvas import SceneCanvas
from .scene_tree_model import SceneTreeModel


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self._setup_ui()
        self.read_settings()
        self.clear_settings()
        self.camera = PerspectiveCamera()
        self.camera.focus = (0, 1.2, 0)
        self.camera.distance = 2
        self.renderer = Renderer()
        self._setup_canvas()
        self.multisample_count = self.sampleCountSpinBox.value()
        self.b_multisample = self.multisampleCheckBox.checkState()
        self.scene_model = SceneTreeModel()
        self.scene_treeView.setModel(self.scene_model)
        self.scene_treeView.setIndexWidget(self.scene_model.index(0, 2), QPushButton('hello'))

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
        self.wireframe_comboBox.activated.connect(self.set_wireframe_mode)

    def _setup_canvas(self):
        self.openGLWidget.camera = self.camera
        self.openGLWidget.renderer = self.renderer

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

    def clear_settings(self):
        settings = QSettings('Brunsgen International', 'glcube')
        settings.setValue('geometry', None)
        settings.setValue('windowState', None)

    def read_settings(self):
        settings = QSettings('Brunsgen International', 'glcube')
        geo = settings.value('geometry')
        if geo:
            self.restoreGeometry(geo)
            self.restoreState(settings.value('windowState'))

    def save_settings(self):
        settings = QSettings('Brunsgen International', 'glcube')
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('windowState', self.saveState())

    def set_multisample_count(self, sample_count):
        self.multisample_count = sample_count
        if self.b_multisample:
            self._change_multisampling(sample_count)

    def set_wireframe_mode(self, mode):
        self.toggle_wireframe(mode != 0)

    def toggle_multisampling(self, checked):
        self.b_multisample = checked
        if checked:
            self._change_multisampling(self.multisample_count)
        else:
            self._change_multisampling(0)

    def toggle_wireframe(self, checked):
        self.lineWidth_doubleSpinBox.setEnabled(checked)
        print('wireframe', checked)
        self.renderer.wireframe = checked
        self.openGLWidget.update()
