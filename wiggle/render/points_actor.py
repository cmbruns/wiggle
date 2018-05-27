import numpy
from OpenGL import GL
from OpenGL.arrays import vbo

from wiggle.material import BaseMaterial
from wiggle.material.texture import Texture
from wiggle.material.shader import ShaderStage, ShaderFileBlock
from wiggle.render.renderer import AutoInitRenderer
from wiggle.render.renderer import VaoRenderer


class PointsMaterial(BaseMaterial):
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
            [ShaderFileBlock('wiggle.glsl', 'positions0.vert'), ],
            GL.GL_VERTEX_SHADER)

    def create_vertex_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'point_texture.frag'), ],
            GL.GL_FRAGMENT_SHADER)

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        self.texture.display_gl(camera=camera, *args, **kwargs)


class PointsActor(AutoInitRenderer, VaoRenderer):
    def __init__(self):
        super().__init__()
        self.points = numpy.array(((0, 0, -1), ), dtype=numpy.float32)
        self.vbo = None
        self.position_location = 0
        self.material = PointsMaterial()

    def init_gl(self):
        super().init_gl()
        self.material.init_gl()
        self.vbo = vbo.VBO(self.points)
        GL.glEnableVertexAttribArray(self.position_location)
        self.vbo.bind()
        GL.glVertexAttribPointer(self.position_location, 3, GL.GL_FLOAT, False, 0, self.vbo)

    def display_gl(self, camera,  *args, **kwargs):
        super().display_gl(camera=camera, *args, **kwargs)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glEnable(GL.GL_BLEND)
        self.material.display_gl(camera=camera, *args, **kwargs)
        self.vbo.bind()
        GL.glEnable(GL.GL_POINT_SPRITE)
        GL.glPointSize(10)
        # GL.glDisable(GL.GL_DEPTH_TEST)
        # print('draw point')
        GL.glDrawArrays(GL.GL_POINTS, 0, self.points.size//3)
