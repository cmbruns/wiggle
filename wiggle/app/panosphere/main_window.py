import pkg_resources

from PyQt5 import uic
from PyQt5.Qt import QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtCore import QSettings

from wiggle.geometry.camera import PerspectiveCamera
from wiggle.render.renderer import Renderer
from wiggle.material.texture import Texture
from wiggle.material.skybox import SkyBoxMaterial
from wiggle.render.skybox_actor import SkyBoxActor


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self._setup_ui()
        self.read_settings()
        self.clear_settings()
        self.camera = PerspectiveCamera()
        self.camera.focus = (0, 0, 0)
        self.camera.distance = 2
        self.renderer = Renderer()
        self._setup_canvas()

    def _quit(self):
        self.save_settings()
        QCoreApplication.quit()

    def _setup_ui(self):
        uic.loadUi(uifile=pkg_resources.resource_stream('wiggle.app.panosphere', 'panosphere.ui'), baseinstance=self)
        self.openGLWidget.main_window = self
        self.actionQuit.triggered.connect(self._quit)
        self.actionOpen.triggered.connect(self.open_file)

    def _setup_canvas(self):
        self.openGLWidget.camera = self.camera
        self.openGLWidget.renderer = self.renderer
        self.openGLWidget.main_window = self

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

    def clear_settings(self):
        settings = QSettings('Brunsgen International', 'panosphere')
        settings.setValue('geometry', None)
        settings.setValue('windowState', None)

    def load_file(self, file_name):
        print(file_name)
        sky_texture = Texture(
            file_name=file_name,
            is_equirectangular=True)
        self.renderer.add_actor(SkyBoxActor(material=SkyBoxMaterial(sky_texture)))
        print("Oops, I don't know how to load files yet.")
        self.openGLWidget.update()

    def open_file(self):
        result = QFileDialog.getOpenFileName(
            parent=self,
            caption='Open a spherical panorama image file now',
            filter='jpeg(*.jpg)',
        )
        if result is None:
            return
        file_name = result[0]
        self.load_file(file_name)

    def read_settings(self):
        settings = QSettings('Brunsgen International', 'panosphere')
        geo = settings.value('geometry')
        if geo:
            self.restoreGeometry(geo)
            self.restoreState(settings.value('windowState'))

    def save_settings(self):
        settings = QSettings('Brunsgen International', 'panosphere')
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('windowState', self.saveState())
