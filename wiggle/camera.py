import math

import numpy

from .matrix import Matrix4f, Matrix3f


class PerspectiveCamera(object):
    def __init__(self):
        self._focus = numpy.array([0, 0, 0], dtype='float32')
        # View matrix
        self.distance = 10
        self.rotation = numpy.identity(4, dtype='float32')
        # Projection
        self.fov_y = math.radians(45.0)
        self._aspect = 1.0
        self.z_near = 0.1
        self.z_far = 100.0
        self._projection = None
        self._projection_needs_update = True
        self._view_matrix = None
        self._view_matrix_needs_update = True

    @property
    def aspect(self):
        return self._aspect

    @aspect.setter
    def aspect(self, aspect):
        self._projection_needs_update = True
        self._aspect = aspect

    @property
    def focus(self):
        return self._focus

    @focus.setter
    def focus(self, xyz):
        self._view_matrix_needs_update = True
        self._focus[:] = xyz

    @property
    def projection(self):
        if self._projection_needs_update:
            self._update_projection()
        return self._projection

    def _update_projection(self):
        m = Matrix4f.perspective(
                fov_y=self.fov_y,
                aspect=self.aspect,
                z_near=self.z_near,
                z_far=self.z_far)
        self._projection = m.pack()
        self._projection_needs_update = False

    def rotate(self, axis, angle):
        r = Matrix4f.rotation(axis, angle)
        self.rotation = self.rotation @ r
        self._view_matrix_needs_update = True

    @property
    def view_matrix(self):
        if self._view_matrix_needs_update:
            self._update_view_matrix()
        return self._view_matrix

    def _update_view_matrix(self):
        translation_a = Matrix4f.translation(0, 0, -self.distance)
        translation_b = Matrix4f.translation(*self._focus)
        m = Matrix4f(translation_b @ self.rotation @ translation_a)

        self._view_matrix = m.pack()
        self._view_matrix_needs_update = False

    def zoom(self, factor):
        self.distance /= factor
        self._view_matrix_needs_update = True
