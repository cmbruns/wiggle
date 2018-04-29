import numpy


class PerspectiveCamera(object):
    def __init__(self):
        self._focus = numpy.array([0, 0, 0], dtype='float32')
        self.distance = 10

    @property
    def focus(self):
        return self._focus

    @focus.setter
    def focus(self, xyz):
        self._focus[:] = xyz
