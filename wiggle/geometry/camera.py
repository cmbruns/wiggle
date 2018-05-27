import math

import numpy

from wiggle.geometry.matrix import Matrix4f


class PerspectiveCamera(object):
    def __init__(self):
        self._focus = numpy.array([0, 0, 0], dtype='float32')
        # View matrix
        self.distance = 10
        self.rotation = numpy.identity(4, dtype='float32')
        # Projection
        self._fov_y = math.radians(45.0)
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
    def fov_y(self):
        return self._fov_y

    @fov_y.setter
    def fov_y(self, fov):
        self._projection_needs_update = True
        self._fov_y = fov

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
        self.rotation = r @ self.rotation
        self._view_matrix_needs_update = True

    def set_y_up(self):
        # Keep rotation matrix near a two-angle version, with y-up-ish
        latitude = math.atan2(self.rotation[2, 1], self.rotation[1, 1])
        r_test = Matrix4f.rotation((1, 0, 0), -latitude)
        r_test = r_test @ self.rotation
        longitude = math.atan2(-r_test[0, 2], r_test[2, 2])
        if latitude > math.radians(90):
            latitude = math.radians(90)
        if latitude < math.radians(-90):
            latitude = math.radians(-90)
        # print(math.degrees(latitude), math.degrees(longitude), r_test[1, 1])
        r1 = Matrix4f.rotation((1, 0, 0), latitude)
        r2 = Matrix4f.rotation((0, 1, 0), -longitude)
        # print(math.degrees(math.atan2(-r2[0, 2], r2[2, 2])))
        self.rotation = r1 @ r2

    @property
    def view_matrix(self):
        if self._view_matrix_needs_update:
            self._update_view_matrix()
        return self._view_matrix

    def _update_view_matrix(self):
        translation_a = Matrix4f.translation(0, 0, -self.distance)
        translation_b = Matrix4f.translation(*-self._focus)
        m = Matrix4f(translation_a @ self.rotation @ translation_b)

        self._view_matrix = m.pack()
        self._view_matrix_needs_update = False

    def zoom(self, factor):
        self.distance /= factor
        self._view_matrix_needs_update = True
