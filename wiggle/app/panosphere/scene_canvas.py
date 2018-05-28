import logging
import math
import pkg_resources
import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QOpenGLWidget, QMenu
from PyQt5.QtGui import QCursor, QPixmap, QSurfaceFormat
import numpy

from wiggle.geometry import normalize
from wiggle.geometry.camera import PerspectiveCamera
from wiggle.geometry.matrix import Matrix4f

_log_level = logging.WARN
logging.basicConfig(level=_log_level)
logger = logging.getLogger(__name__)
logger.setLevel(_log_level)


class CenterOnPointAction(QAction):
    def __init__(self, location_w, scene_canvas):
        super().__init__()
        self.setText('Center On This Location')
        self.scene_canvas = scene_canvas
        self.location_w = location_w
        self.triggered.connect(self.center_on)

    def center_on(self):
        self.scene_canvas.center_on(self.location_w)


class MouseClickManager(object):
    def __init__(self, widget):
        self.widget = widget
        self.pressed_time = None
        self.previous_pressed_time = None
        self.pressed_pos = None

    def clear(self):
        self.pressed_time = None
        self.pressed_pos = None

    def mouse_pressed(self, event):
        self.pressed_time = datetime.datetime.now()
        self.pressed_pos = event.pos()

    def mouse_released(self, event):
        if self.pressed_time is None:
            return
        released_time = datetime.datetime.now()
        elapsed = (released_time - self.pressed_time).total_seconds()
        if elapsed > 0.9:
            self.clear()
            return
        released_pos = event.pos()
        delta_pos = released_pos - self.pressed_pos
        if delta_pos.manhattanLength() > 5:
            self.clear()
            return
        if self.previous_pressed_time is not None:
            # A double click is just a click
            if (self.pressed_time - self.previous_pressed_time).total_seconds() < 0.5:
                self.clear()
                return
        self.previous_pressed_time = released_time
        self.widget.mouse_click_event(self.pressed_pos, event)
        self.clear()


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
        #
        cursor_file_name = pkg_resources.resource_filename('wiggle.images', 'cross-hair.png')
        cursor_pixmap = QPixmap(cursor_file_name)
        cross_hair_cursor = QCursor(cursor_pixmap, 15, 15)
        self.setCursor(cross_hair_cursor)
        self.click_manager = MouseClickManager(self)
        self.setMouseTracking(True)  # Hover event
        self.main_window = None

    def center_on(self, position_w):
        a = position_w
        b = self._world_direction_from_screen_pixel(self.width()/2, self.height()/2)
        # b = (0, 0, -1)  # target center position
        rotation_axis = normalize(numpy.cross(a, b))
        cosangle = numpy.dot(a, b)
        cosangle = min(cosangle, 1.0)
        cosangle = max(cosangle, -1.0)
        rotation_angle = math.acos(cosangle)
        rot = Matrix4f.rotation(rotation_axis, rotation_angle)
        self.camera.rotation = self.camera.rotation @ rot
        self.camera.set_y_up()
        self.update()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        world_pos = self._world_direction_from_screen_pixel(event.pos().x(), event.pos().y())
        center_on_point_action = CenterOnPointAction(world_pos, self)
        menu.addAction(center_on_point_action)
        menu.addAction('Reset View', self.reset_view)
        menu.addSeparator()
        menu.addAction('Close This Menu')
        menu.exec(event.globalPos())

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

    def mouse_click_event(self, press_position, release_event):
        pass  # todo:

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            # Drag scene with mouse
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
            self.camera.set_y_up()
            self.update()
        else:
            # Hover to show mouse location
            p_world = self._world_direction_from_screen_pixel(event.pos().x(), event.pos().y())
            self.main_window.statusbar.showMessage('x=%+4.2f, y=%+4.2f, z=%+4.2f' % (p_world[0], p_world[1], p_world[2]))

    def _world_direction_from_screen_pixel(self, x, y):
        p_ndc = (2 * x / self.width() - 1, -2 * y / self.height() + 1)
        p_view = numpy.linalg.inv(self.camera.projection) @ (p_ndc[0], p_ndc[1], 0.5, 1.0)
        p_view = normalize(p_view[:3])
        # todo: rotation
        p_world = numpy.linalg.inv(self.camera.view_matrix) @ (p_view[0], p_view[1], p_view[2], 0)
        return p_world[:3]

    def mousePressEvent(self, event):
        if self.is_dragging:
            return  # Who cares?
        self.click_manager.mouse_pressed(event)
        if event.buttons() & Qt.LeftButton:
            self.is_dragging = True
            self.mouse_location = event.pos()

    def mouseReleaseEvent(self, event):
        self.click_manager.mouse_released(event)
        if event.button() == Qt.LeftButton:
            self.is_dragging = False

    def paintGL(self):
        if self.renderer is not None:
            self.renderer.display_gl(camera=self.camera)

    def reset_view(self):
        self.camera.rotation = Matrix4f.identity()
        self.camera.fov_y = math.radians(45)
        self.update()

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
        new_fov = self.camera.fov_y / zoom
        if new_fov > math.radians(130):
            new_fov = math.radians(130)
        self.camera.fov_y = new_fov
        self.update()
