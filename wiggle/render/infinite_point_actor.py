import numpy
from OpenGL import GL
from OpenGL.arrays import vbo

from wiggle.material import BaseMaterial
from wiggle.material.texture import Texture
from wiggle.material.shader import ShaderStage, ShaderFileBlock
from wiggle.render.base import RenderPassType
from wiggle.render.renderer import AutoInitRenderer
from wiggle.render.renderer import VaoRenderer


class InfinitePointMaterial(BaseMaterial):
    def __init__(self, texture=None):
        super().__init__()
        if texture is None:
            texture = Texture(
                file_name='Point70.png',
                package='wiggle.app.panosphere.images',
                is_equirectangular=False)
        self.texture = texture

    def create_vertex_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'infinite_point.vert'), ],
            GL.GL_VERTEX_SHADER)

    def create_vertex_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'point_texture.frag'), ],
            GL.GL_FRAGMENT_SHADER)

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        self.texture.display_gl(camera=camera, *args, **kwargs)


class InfinitePointActor(AutoInitRenderer, VaoRenderer):
    def __init__(self):
        super().__init__(render_pass=RenderPassType.GROUND)
        self.points = numpy.array(((0, 0, -1), ), dtype=numpy.float32)
        self.vbo = None
        self.position_location = 0
        self.material = InfinitePointMaterial()

    def init_gl(self):
        super().init_gl()
        self.material.init_gl()
        self.vbo = vbo.VBO(self.points)
        GL.glEnableVertexAttribArray(self.position_location)
        self.vbo.bind()
        GL.glVertexAttribPointer(self.position_location, 3, GL.GL_FLOAT, False, 0, self.vbo)

    def display_gl(self, camera,  *args, **kwargs):
        super().display_gl(camera=camera, *args, **kwargs)
        self.material.display_gl(camera=camera, *args, **kwargs)
        self.vbo.bind()
        GL.glEnable(GL.GL_POINT_SPRITE)
        GL.glPointSize(10)
        GL.glDrawArrays(GL.GL_POINTS, 0, self.points.size//3)
