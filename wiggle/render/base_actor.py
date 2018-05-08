from OpenGL import GL

from wiggle.render.renderer import AutoInitRenderer
from wiggle.geometry.matrix import ModelMatrix


class BaseActor(AutoInitRenderer):
    def __init__(self):
        super().__init__()
        self.shader = 0
        self.model_matrix = ModelMatrix()

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        GL.glUseProgram(self.shader)
        GL.glUniformMatrix4fv(0, 1, False, camera.projection)
        model_view = self.model_matrix @ camera.view_matrix
        GL.glUniformMatrix4fv(4, 1, False, model_view.pack())

    def dispose_gl(self):
        GL.glDeleteProgram(self.shader)
        self.shader = 0
        super().dispose_gl()

    @property
    def model_center(self):
        return self._model_matrix.model_center

    @model_center.setter
    def model_center(self, center):
        self.model_matrix.model_center = center

    @property
    def scale(self):
        return self._model_matrix.scale

    @scale.setter
    def scale(self, scale):
        self.model_matrix.scale = scale
