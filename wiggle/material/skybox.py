from OpenGL import GL

from wiggle.material import BaseMaterial
from wiggle.material.shader import ShaderStage, ShaderFileBlock
from wiggle.material.texture import Texture


class NothingMaterial(BaseMaterial):
    def display_gl(self, camera, *args, **kwargs):
        pass


class SkyBoxMaterial(BaseMaterial):
    def __init__(self):
        super().__init__()
        self.texture = Texture('wiggle.images', 'xerox_office.jpg', is_equirectangular=True)

    def create_vertex_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'skybox.vert'), ],
            GL.GL_VERTEX_SHADER)

    def create_fragment_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'skybox.frag'), ],
            GL.GL_FRAGMENT_SHADER)

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        self.texture.display_gl(camera=camera, *args, **kwargs)
