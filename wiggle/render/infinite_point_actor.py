from enum import Enum

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


class PointStyle(Enum):
    BASIC = 1
    ADJUSTED = 2
    HOVERED = 3


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

    def create_fragment_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'point_texture.frag'), ],
            GL.GL_FRAGMENT_SHADER)

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        self.texture.display_gl(camera=camera, *args, **kwargs)


class InfinitePointActor(BaseActor, VaoRenderer):
    def __init__(self):
        super().__init__(render_pass=RenderPassType.GROUND)
        self.points = [(0, 0, -1.0), ]
        self.styles = [PointStyle.BASIC.value, ]
        self.vbo = vbo.VBO(numpy.array(self.points, dtype=numpy.float32))
        self.vbo_styles = vbo.VBO(numpy.array(self.styles, dtype=numpy.uint8))
        self.position_location = 0
        self.style_location = 2
        self.material = InfinitePointMaterial()

    def add_point(self, x, y, z, style=PointStyle.BASIC):
        self.points = numpy.append(arr=self.points, values=numpy.array(((x, y, z),), dtype=numpy.float32), axis=0)
        self.styles.append(style.value)
        self.update_points()

    def update_points(self):
        self.vbo.set_array(numpy.array(self.points, dtype=numpy.float32))
        self.vbo_styles.set_array(numpy.array(self.styles, dtype=numpy.uint8))

    def set_only_point(self, x, y, z):
        self.points = numpy.array(((x, y, z), ), dtype=numpy.float32)
        self.vbo.set_array(self.points)

    def init_gl(self):
        super().init_gl()
        GL.glEnableVertexAttribArray(self.position_location)
        self.vbo.bind()
        GL.glVertexAttribPointer(self.position_location, 3, GL.GL_FLOAT, False, 0, self.vbo)
        self.vbo_styles.bind()
        GL.glEnableVertexAttribArray(self.style_location)
        GL.glVertexAttribIPointer(self.style_location, 1, GL.GL_UNSIGNED_BYTE, 0, self.vbo_styles)

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
        self.vbo_styles.bind()
        GL.glEnable(GL.GL_POINT_SPRITE)
        GL.glEnable(GL.GL_VERTEX_PROGRAM_POINT_SIZE)
        GL.glDrawArrays(GL.GL_POINTS, 0, self.points.size//3)
