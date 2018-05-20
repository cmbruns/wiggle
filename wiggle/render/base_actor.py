from OpenGL import GL

from wiggle.render.renderer import AutoInitRenderer
from wiggle.geometry.matrix import ModelMatrix


class BaseActor(AutoInitRenderer):
    def __init__(self):
        super().__init__()
        self.model_matrix = ModelMatrix()

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)

    def dispose_gl(self):
        super().dispose_gl()

    @property
    def model_center(self):
        return self.model_matrix.model_center

    @model_center.setter
    def model_center(self, center):
        self.model_matrix.model_center = center

    @property
    def model_rotation(self):
        return self.model_matrix.model_rotation

    @model_rotation.setter
    def model_rotation(self, rotation):
        self.model_matrix.model_rotation = rotation

    @property
    def model_scale(self):
        return self.model_matrix.model_scale

    @model_scale.setter
    def model_scale(self, scale):
        self.model_matrix.model_scale = scale
