import numpy
from OpenGL import GL
from OpenGL.arrays import vbo

from wiggle.geometry.matrix import Matrix4f
from wiggle.material import BaseMaterial
from wiggle.material.texture import Texture
from wiggle.material.shader import ShaderStage, ShaderFileBlock
from wiggle.render.base import RenderPassType
from wiggle.render.base_actor import BaseActor
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
        self.color = numpy.array((0.8, 0.8, 0.8), dtype=numpy.float32)
        self.color_location = None

    def create_vertex_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'infinite_point.vert'), ],
            GL.GL_VERTEX_SHADER)

    def create_fragment_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'point_texture.frag'), ],
            GL.GL_FRAGMENT_SHADER)

    def init_gl(self):
        super().init_gl()
        self.color_location = GL.glGetUniformLocation(self.shader, 'color')

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        GL.glUniform3f(self.color_location, *self.color)
        self.texture.display_gl(camera=camera, *args, **kwargs)


class InfinitePointActor(BaseActor, VaoRenderer):
    def __init__(self):
        super().__init__(render_pass=RenderPassType.GROUND)
        self.points = numpy.array(((0, 0, -1.0), (0, 1, 0), ), dtype=numpy.float32)
        self.vbo = vbo.VBO(self.points)
        self.position_location = 0
        self.material = InfinitePointMaterial()
        self.point_size = 13

    def add_point(self, x, y, z):
        self.points = numpy.append(arr=self.points, values=numpy.array(((x, y, z),), dtype=numpy.float32), axis=0)
        self.vbo.set_array(self.points)

    @property
    def color(self):
        return self.material.color

    @color.setter
    def color(self, rgb):
        self.material.color = numpy.array(rgb, dtype=numpy.float32)

    def set_only_point(self, x, y, z):
        self.points = numpy.array(((x, y, z), ), dtype=numpy.float32)
        self.vbo.set_array(self.points)

    def init_gl(self):
        super().init_gl()
        GL.glEnableVertexAttribArray(self.position_location)
        self.vbo.bind()
        GL.glVertexAttribPointer(self.position_location, 3, GL.GL_FLOAT, False, 0, self.vbo)

    def display_gl(self, camera,  *args, **kwargs):
        if not self.is_visible:
            return
        super().display_gl(camera=camera, *args, **kwargs)
        self.material.display_gl(camera=camera, *args, **kwargs)
        for name, location in self.material.mvp_matrices.items():
            if name == 'projection':
                GL.glUniformMatrix4fv(location, 1, True, camera.projection)
            elif name == 'model':
                GL.glUniformMatrix4fv(location, 1, True, self.model_matrix.matrix)
            elif name == 'view':
                GL.glUniformMatrix4fv(location, 1, True, camera.view_matrix)
            elif name == 'model_view':
                GL.glUniformMatrix4fv(location, 1, True, Matrix4f(camera.view_matrix @ self.model_matrix.matrix).pack())
        self.vbo.bind()
        GL.glEnable(GL.GL_POINT_SPRITE)
        GL.glPointSize(self.point_size)
        GL.glDrawArrays(GL.GL_POINTS, 0, self.points.size//3)
