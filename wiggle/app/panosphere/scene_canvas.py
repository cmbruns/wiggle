import logging
import math

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QSurfaceFormat

from wiggle.geometry.camera import PerspectiveCamera

_log_level = logging.WARN
logging.basicConfig(level=_log_level)
logger = logging.getLogger(__name__)
logger.setLevel(_log_level)


class PanosphereSceneCanvas(QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_dragging = False
        self.mouse_location = None
        self.renderer = None
        self.camera = PerspectiveCamera()
        format_ = QSurfaceFormat()
        format_.setSamples(4)
        self.setFormat(format_)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_name = url.toLocalFile()
            self.main_window.load_file(file_name)

    def initializeGL(self):
        super().initializeGL()
        if self.renderer is not None:
            self.renderer.init_gl()

    def mouseMoveEvent(self, event):
        if not self.is_dragging:
            return
        p1 = event.pos()
        p0 = self.mouse_location
        self.mouse_location = p1
        dx = p1.x() - p0.x()
        dy = p1.y() - p0.y()
        radians_per_pixel = self.camera.fov_y / self.height()
        dist_pixels = math.sqrt(dx*dx + dy*dy)
        if dist_pixels == 0:
            return
        dist_radians = dist_pixels * radians_per_pixel
        rotation_axis = (dy/dist_pixels, dx/dist_pixels, 0)
        self.camera.rotate(rotation_axis, -dist_radians)
        self.camera.set_up_direction = (0, 1, 0)  # todo: the goggles do nothing
        self.update()

    def mousePressEvent(self, event):
        if self.is_dragging:
            return  # Who cares?
        if event.buttons() & Qt.LeftButton:
            self.is_dragging = True
            self.mouse_location = event.pos()

    def mouseReleaseEvent(self, event):
        if not self.is_dragging:
            return  # Who cares?
        if event.button() == Qt.LeftButton:
            self.is_dragging = False

    def paintGL(self):
        if self.renderer is not None:
            self.renderer.display_gl(camera=self.camera)

    def resizeGL(self, width, height):
        aspect = width / float(height)
        self.camera.aspect = aspect

    def set_canvas_size(self, width, height):
        while self.width() != width or self.height() != height:
            dw = width - self.width()
            dh = height - self.height()
            mw = self.main_window.width() + dw
            mh = self.main_window.height() + dh
            self.main_window.resize(mw, mh)

    def wheelEvent(self, event):
        degrees = event.angleDelta().y() / 8.0
        zoom = 1.003 ** degrees
        # todo: zoom should change the field of view
        self.camera.fov_y *= zoom
        self.update()
