import numpy


class Vec3(object):
    def __init__(self, x, y, z):
        self._arr = numpy.array((x, y, z), dtype=numpy.float32)

    # Sequence operations

    def __getitem__(self, key):
        return self._arr[key]

    def __len__(self):
        return 3

    # Arithmetic operations

    def __add__(self, rhs):
        return Vec3(*(self._arr + rhs))

    def __mul__(self, rhs):
        return Vec3(*(self._arr * rhs))

    def __sub__(self, rhs):
        return Vec3(*(self._arr - rhs))

    def __truediv__(self, rhs):
        return Vec3(*(self._arr / rhs))

    def dot(self, rhs):
        return numpy.dot(self._arr, rhs)

    def norm(self):
        return numpy.linalg.norm(self._arr)


def normalize(v):
    # norm = v.norm()
    norm = numpy.linalg.norm(v)
    return v * 1.0/norm
