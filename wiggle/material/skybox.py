from OpenGL import GL

from wiggle.material import BaseMaterial
from wiggle.material.shader import ShaderStage, ShaderFileBlock
from wiggle.material.texture import Texture


class SkyBoxMaterial(BaseMaterial):
    def __init__(self, texture=None):
        super().__init__()
        if texture is None:
            texture = Texture(
                file_name='_0010782_stitch2.jpg',
                package='wiggle.images',
                is_equirectangular=True)
        self.texture = texture

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
