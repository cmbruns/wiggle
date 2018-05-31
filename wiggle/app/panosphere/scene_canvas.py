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
from wiggle.render.infinite_point_actor import InfinitePointActor

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
        self.setMouseTracking(True)  # Hover event
        self.main_window = None
        self.hover_actor = None
        self.has_hover_effect = False

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
        md = event.mimeData()
        if md.hasFormat('application/x-vertical-line'):
            # print('vertical line drag')
            event.acceptProposedAction()
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('application/x-vertical-line'):
            pos = self._world_direction_from_screen_pixel(event.pos().x(), event.pos().y())
            dy = 0.1 * self.camera.fov_y
            upper_spot = normalize(pos + (0, dy, 0))
            lower_spot = normalize(pos - (0, dy, 0))
            self.main_window.panosphere.add_vertical_line(upper_spot, lower_spot)
            self.update()
        for url in event.mimeData().urls():
            file_name = url.toLocalFile()
            self.main_window.load_file(file_name)

    def initializeGL(self):
        super().initializeGL()
        if self.renderer is not None:
            self.renderer.init_gl()

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
            tol = 8 * self.camera.fov_y / self.height()
            close_point = self.main_window.panosphere.point_near(*p_world, tol)
            if close_point is None:
                # unhover
                if self.hover_actor is not None:
                    self.hover_actor.is_visible = False
                    if self.has_hover_effect:
                        self.has_hover_effect = False
                        self.update()
            else:
                # hover to enlarge point
                if self.hover_actor is None:
                    self.hover_actor = InfinitePointActor()
                    self.hover_actor.point_size = 20
                    self.hover_actor.color = (1, 1, 0.5)
                    self.renderer.add_actor(self.hover_actor)
                self.hover_actor.set_only_point(*close_point)
                self.hover_actor.is_visible = True
                self.has_hover_effect = True
                self.update()

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
        if event.buttons() & Qt.LeftButton:
            self.is_dragging = True
            self.mouse_location = event.pos()

    def mouseReleaseEvent(self, event):
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
