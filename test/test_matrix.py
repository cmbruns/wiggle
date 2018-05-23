import unittest
from math import radians

from wiggle.geometry.matrix import Matrix4f, Matrix3f


class TestMatrix(unittest.TestCase):
    def test_rotation(self):
        v = Matrix4f.rotation((1, 0, 0), radians(10)) @ (0, 1, 0, 0)
        self.assertGreater(v[2], 0)
        v = Matrix3f.rotation((1, 0, 0), radians(10)) @ (0, 1, 0)
        self.assertGreater(v[2], 0)
        v = Matrix4f.rotation((0, 1, 0), radians(10)) @ (0, 0, 1, 0)
        self.assertGreater(v[0], 0)
        v = Matrix3f.rotation((0, 1, 0), radians(10)) @ (0, 0, 1)
        self.assertGreater(v[0], 0)
        v = Matrix4f.rotation((0, 0, 1), radians(10)) @ (0, 1, 0, 0)
        self.assertLess(v[0], 0)
        v = Matrix3f.rotation((0, 0, 1), radians(10)) @ (0, 1, 0)
        self.assertLess(v[0], 0)

    def test_scale(self):
        v = Matrix4f.scale(2) @ (0, 1, 0, 0)
        self.assertGreater(v[1], 1.8)
        v = Matrix3f.scale(2) @ (0, 1, 0)
        self.assertGreater(v[1], 1.8)

    def test_translation(self):
        v = Matrix4f.translation(1, 0, 0) @ (0, 0, 0, 1)
        self.assertGreater(v[0], 0.9)

    def test_rotation_translation(self):
        v = Matrix4f.translation(1, 0, 0) @ Matrix4f.rotation((1, 0, 0), radians(10)) @ (0, 0, 0, 1)
        self.assertAlmostEqual(v[0], 1)
