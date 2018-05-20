import math

import numpy


class MatrixBase(object):
    def __init__(self, matrix=numpy.identity(4)[:]):
        self.m = numpy.array(matrix[:], dtype=numpy.float32)

    def __getitem__(self, item):
        return self.m[item]

    def __imatmul__(self, other):
        self.m @= other[:]

    def __matmul__(self, rhs):
        result = rhs @ self.m
        return self.__class__(result[:])

    def __mul__(self, rhs):
        result = rhs * self.m
        return self.__class__(result[:])

    def __len__(self):
        return len(self.m)

    def __rmul__(self, lhs):
        result = lhs * self.m
        return self.__class__(result[:])

    def pack(self, do_transpose=False):
        if do_transpose:
            return numpy.ascontiguousarray(self.m.T)
        else:
            return numpy.ascontiguousarray(self.m)

    def transpose(self):
        return self.__class__(self.m.T)


class Matrix3f(MatrixBase):
    @classmethod
    def identity(cls):
        return cls(numpy.identity(3)[:])

    @classmethod
    def rotation(cls, axis, radians):
        c = math.cos(radians)
        s = math.sin(radians)
        t = 1 - c
        x, y, z = axis[:]
        return cls(
            ((t*x*x + c,  t*x*y - s*z, t*x*z + s*y),
             (t*x*y + s*z, t*y*y + c,  t*y*z - s*x),
             (t*x*z - s*y, t*y*z + s*x, t*z*z + c))
        )

    @classmethod
    def scale(cls, scale):
        return cls(
            ((scale, 0, 0),
             (0, scale, 0),
             (0, 0, scale))
        )


class Matrix4f(MatrixBase):
    def __init__(self, matrix=numpy.identity(4)[:]):
        super().__init__(matrix)

    def __matmul__(self, rhs):
        if len(rhs) == 3:
            # homogeneous matrix times vector
            foo = list(rhs[:])
            foo.extend([1.0, ], )
            rhs = numpy.array(foo, dtype=numpy.float32)
        return Matrix4f(self.m @ rhs)

    @classmethod
    def frustum(cls, left, right, bottom, top, z_near, z_far):
        a = (right + left) / (right - left)
        b = (top + bottom) / (top - bottom)
        c = - (z_far + z_near) / (z_far - z_near)
        d = - (2.0 * z_far * z_near) / (z_far - z_near)
        return cls(
                ((2.0 * z_near / (right - left), 0, 0, 0),
                 (0, 2.0 * z_near / (top - bottom), 0, 0),
                 (a, b, c, -1),
                 (0, 0, d, 0),)
        )

    @classmethod
    def identity(cls):
        return cls(numpy.identity(4)[:])

    @classmethod
    def orthographic(cls, l, r, b, t, n, f):
        return cls([
            [2.0 / (r - l), 0, 0, -(r + l) / (r - l)],
            [0, 2.0 / (t - b), 0, -(t + b) / (t - b)],
            [0, 0, -2.0 / (f - n), -(f + n) / (f - n)],
            [0, 0, 0, 1]]).transpose()

    @classmethod
    def perspective(cls, fov_y=math.radians(35.0), aspect=1.0, z_near=0.1, z_far=100.0):
        # Negate vertical, because screen Y is down, and OpenGL Y is up
        top = z_near * math.tan(fov_y / 2.0)
        right = top * aspect
        return cls.frustum(-right, right, -top, top, z_near, z_far)

    @classmethod
    def rotation(cls, axis, radians):
        c = math.cos(radians)
        s = math.sin(radians)
        t = 1 - c
        x, y, z = axis[:]
        return cls(
            ((t*x*x + c,  t*x*y - s*z, t*x*z + s*y, 0),
             (t*x*y + s*z, t*y*y + c,  t*y*z - s*x, 0),
             (t*x*z - s*y, t*y*z + s*x, t*z*z + c, 0),
             (0, 0, 0, 1),)
        ).transpose()

    @classmethod
    def scale(cls, scale):
        return cls(
            ((scale, 0, 0, 0),
             (0, scale, 0, 0),
             (0, 0, scale, 0),
             (0, 0, 0, 1),)
        )

    @classmethod
    def translation(cls, x, y, z):
        return cls(
            ((1, 0, 0, 0),
             (0, 1, 0, 0),
             (0, 0, 1, 0),
             (x, y, z, 1),)
        )


class ModelMatrix(object):
    def __init__(self):
        self._center = numpy.array([0, 0, 0], dtype='float32')
        self._scale = 1.0
        self._rotation = Matrix4f.identity()
        self._needs_update = True
        self._matrix = None

    def __matmul__(self, rhs):
        return Matrix4f(self.matrix @ rhs)

    @property
    def matrix(self):
        if self._needs_update:
            self._matrix = (Matrix4f.scale(self._scale) @ self._rotation @ Matrix4f.translation(*self._center)).pack()
        return self._matrix

    @property
    def model_center(self):
        return self._center

    @model_center.setter
    def model_center(self, center):
        self._needs_update = True
        self._center[:] = center[:]

    @property
    def model_rotation(self):
        return self._rotation

    @model_rotation.setter
    def model_rotation(self, rotation):
        self._needs_update = True
        self._rotation = rotation

    @property
    def model_scale(self):
        return self._scale

    @model_scale.setter
    def model_scale(self, scale):
        self._needs_update = True
        self._scale = scale
