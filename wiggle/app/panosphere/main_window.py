import pkg_resources

from PyQt5 import uic
from PyQt5.Qt import QCoreApplication
from PyQt5.QtCore import QMimeData, QSettings, Qt, QPoint
from PyQt5.QtGui import QDrag, QPixmap
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from wiggle.app.panosphere.panosphere import Panosphere
from wiggle.geometry.camera import PerspectiveCamera
from wiggle.app.recent_file import RecentFileList
from wiggle.render.renderer import Renderer


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self._setup_ui()
        self.camera = PerspectiveCamera()
        self.camera.focus = (0, 0, 0)
        self.camera.distance = 2
        #
        self.renderer = Renderer()
        self._setup_canvas()
        self.panosphere = Panosphere()
        self.renderer.add_actor(self.panosphere.actor)
        #
        self.recent_files = RecentFileList(
            open_file_slot=self.load_file,
            settings_key='recent_files',
            menu=self.menuRecent_Files,
            app_name='panosphere',
        )

    def _setup_ui(self):
        uic.loadUi(uifile=pkg_resources.resource_stream('wiggle.app.panosphere', 'panosphere.ui'), baseinstance=self)
        self.read_settings()
        self.clear_settings()
        self.openGLWidget.main_window = self

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
        self.recent_files.add_file(file_name)
        self.panosphere.add_image(file_name)
        self.openGLWidget.update()

    def on_actionOpen_triggered(self, checked=None):
        # Avoid calling twice by responding only to the zero-argument version
        if checked is not None:
            return
        result = QFileDialog.getOpenFileName(
            parent=self,
            caption='Open a spherical panorama image file now',
            filter='All Files (*.*);;Images (*.jpg *.ktx)',
            initialFilter='Images (*.jpg *.ktx)',
        )
        if result is None:
            return
        file_name = result[0]
        if len(file_name) < 1:
            return
        self.load_file(file_name)

    def on_actionQuit_triggered(self, checked=None):
        # Avoid calling twice by responding only to the zero-argument version
        if checked is not None:
            return
        self.save_settings()
        QCoreApplication.quit()

    def on_actionReset_View_triggered(self, checked=None):
        # Avoid calling twice by responding only to the zero-argument version
        if checked is not None:
            return
        self.openGLWidget.reset_view()

    def on_verticalLineButton_pressed(self):
        mime_data = QMimeData()
        mime_data.setData('application/x-vertical-line', b'vertical line')
        mime_data.setText(self.verticalLineButton.text())
        drag = QDrag(self.verticalLineButton)
        drag.setMimeData(mime_data)
        pixmap = QPixmap(pkg_resources.resource_filename('wiggle.app.panosphere.images', 'VerticalLine32.png'))
        drag.setHotSpot(QPoint(16, 4))
        drag.setPixmap(pixmap)
        drag.exec(Qt.CopyAction)

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
