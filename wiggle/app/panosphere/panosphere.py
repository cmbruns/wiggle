from wiggle.geometry import normalize
from wiggle.geometry import Vec3
from wiggle.material.skybox import SkyBoxMaterial
from wiggle.material.texture import Texture
from wiggle.render.base import RenderPassType
from wiggle.render.base_actor import BaseActor
from wiggle.render.infinite_point_actor import InfinitePointActor
from wiggle.render.skybox_actor import SkyBoxActor


class PanoActor(BaseActor):
    def __init__(self):
        super().__init__(render_pass=RenderPassType.SKY)
        self.points_actor = InfinitePointActor()
        self.points_actor.add_point(1, 0, 0)
        self.image_actors = []

    def add_image(self, file_name):
        sky_texture = Texture(
            file_name=file_name,
            is_equirectangular=True)
        self.image_actors.append(SkyBoxActor(material=SkyBoxMaterial(sky_texture)))

    def display_gl(self, *args, **kwargs):
        for image in self.image_actors:
            image.display_gl(*args, **kwargs)
        self.points_actor.display_gl(*args, **kwargs)


class PanoPoint(object):
    def __init__(self, x, y, z):
        self.direction = normalize(Vec3(x, y, z), )

    # Sequence operations

    def __getitem__(self, key):
        return self.direction[key]

    def __len__(self):
        return len(self.direction)

    # Arithmetic operations

    def __sub__(self, rhs):
        return self.direction - rhs

    def __mul__(self, rhs):
        return self.direction * rhs


class Panosphere(object):
    def __init__(self):
        self._points = []
        self._vertical_lines = []
        self.actor = PanoActor()

    def add_image(self, file_name):
        self.actor.add_image(file_name)

    def add_vertical_line(self, point1, point2):
        p1 = PanoPoint(*point1)
        p2 = PanoPoint(*point2)
        self._vertical_lines.append(VerticalLine(p1, p2))
        self._points.append(p1)
        self._points.append(p2)
        self.actor.points_actor.add_point(*point1)
        self.actor.points_actor.add_point(*point2)

    def point_near(self, x, y, z, tolerance):
        # todo: use a more sophisticated spatial index
        d2_max = tolerance * tolerance
        d2_min = None
        best_point = None
        for p in self._points:
            dv = p - (x, y, z)
            test2 = dv.dot(dv)
            if test2 > d2_max:
                continue
            if d2_min is None:
                d2_min = test2
                best_point = p
                continue
            if test2 < d2_min:
                d2_min = test2
                best_point = p
        return best_point


class VerticalLine(object):
    def __init__(self, point1, point2):
        self.points = [point1, point2]


