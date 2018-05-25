from OpenGL import GL

from wiggle.material import BaseMaterial
from wiggle.material.shader import ShaderStage, ShaderFileBlock
from wiggle.material.texture import Texture


class SkySphereMaterial(BaseMaterial):
    def __init__(self):
        super().__init__()
        self.texture = Texture('wiggle.images', 'R0010347.JPG', is_equirectangular=True)

    def create_vertex_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'skysphere.vert'), ],
            GL.GL_VERTEX_SHADER)

    def create_fragment_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'skysphere.frag'), ],
            GL.GL_FRAGMENT_SHADER)

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        self.texture.display_gl(camera=camera, *args, **kwargs)
