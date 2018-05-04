import numpy
from numpy import array, asarray, dot
import math

_identity4 = (
    (1, 0, 0, 0),
    (0, 1, 0, 0),
    (0, 0, 1, 0),
    (0, 0, 0, 1))

_identity3 = (
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1))


class MatrixBase(object):
    def __init__(self, matrix=_identity3):
        super().__init__(matrix)

    def __init__(self, matrix=_identity4):
        self.m = numpy.array(matrix[:], dtype=numpy.float32)

    def __getitem__(self, item):
        return self.m[item]

    def __imul__(self, other):
        self.m = numpy.dot(self[:], other[:])

    def __len__(self):
        return len(self.m)

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


class Matrix3f(MatrixBase):
    def __mul__(self, rhs):
        return Matrix3f(numpy.dot(self[:], rhs[:]))


class Matrix4f(MatrixBase):
    def __init__(self, matrix=_identity4):
        super().__init__(matrix)

    def __mul__(self, rhs):
        if len(rhs) == 3:
            # homogeneous matrix times vector
            foo = list(rhs[:])
            foo.extend([1.0, ], )
            rhs = numpy.array(foo, dtype=numpy.float32)
        return Matrix4f(numpy.dot(self[:], rhs[:]))

    @classmethod
    def frustum(cls, left, right, top, bottom, z_near, z_far):
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
        return cls(numpy.identity(4))

    def pack(self, do_transpose=False):
        if do_transpose:
            return numpy.ascontiguousarray(self.m.T)
        else:
            return numpy.ascontiguousarray(self.m)

    @classmethod
    def perspective(cls, fov_y=math.radians(35.0), aspect=1.0, z_near=0.1, z_far=100.0):
        # Negate vertical, because screen Y is down, and OpenGL Y is up
        fh = -z_near * math.tan(fov_y / 2.0)
        fw = -fh * aspect
        return cls.frustum(-fw, fw, -fh, fh, z_near, z_far)

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
        )

    @classmethod
    def translation(cls, x, y, z):
        return cls(
            ((1, 0, 0, 0),
             (0, 1, 0, 0),
             (0, 0, 1, 0),
             (x, y, z, 1),)
        )

    def transpose(self):
        return Matrix4f(self.m.T)


class ModelMatrix(Matrix4f):
    def __init__(self):
        self._center = array([0, 0, 0], dtype='float32')
        self._needs_update = True
        self._matrix = None

    def __matmul__(self, rhs):
        return Matrix4f(self.matrix @ rhs)

    @property
    def matrix(self):
        if self._needs_update:
            self._matrix = Matrix4f.translation(*self._center).pack()
        return self._matrix

    @property
    def model_center(self):
        return self._center

    @model_center.setter
    def model_center(self, center):
        self._needs_update = True
        self._center[:] = center[:]


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.

    from https://stackoverflow.com/questions/6802577/rotation-of-3d-vector
    """
    axis = asarray(axis)
    axis = axis/math.sqrt(dot(axis, axis))
    a = math.cos(theta/2.0)
    b, c, d = -axis*math.sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                  [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                  [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])


def main():
    v = [3, 5, 0]
    axis = [4, 4, 1]
    theta = 1.2
    print(dot(rotation_matrix(axis, theta), v))
    # [ 2.74911638  4.77180932  1.91629719]


if __name__ == '__main__':
    main()
