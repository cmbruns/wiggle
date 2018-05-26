from enum import Enum

from OpenGL import GL

import numpy

from wiggle.material import BaseMaterial
from wiggle.material.shader import ShaderStage, ShaderFileBlock
from wiggle.material.texture import Texture


class PlaneMaterial(BaseMaterial):
    class RenderMode(Enum):
        """
        Synchronize these values with those in plane.frag
        """
        # todo: abstract these to another type of class
        SOLID = 0
        TEXTURE = 1
        CHECKER = 2
        TEX_COORD = 3
        EQUIRECTANGULAR = 4

    def __init__(self):
        super().__init__()
        self.render_mode_index = None
        self.render_mode = self.RenderMode.EQUIRECTANGULAR
        self.texture = Texture(
            file_name='R0010347.jpg',
            package='wiggle.images',
            is_equirectangular=True)

    def create_vertex_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'plane.vert'), ],
            GL.GL_VERTEX_SHADER)

    def create_fragment_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'plane.frag'), ],
            GL.GL_FRAGMENT_SHADER)

    def display_gl(self, *args, **kwargs):
        super().display_gl(*args, **kwargs)
        GL.glEnable(GL.GL_CLIP_PLANE0)
        #
        GL.glUniform1i(self.render_mode_index, self.render_mode.value)
        if self.render_mode == self.RenderMode.TEXTURE or self.render_mode == self.RenderMode.EQUIRECTANGULAR:
            self.texture.display_gl(*args, **kwargs)

    def init_gl(self):
        super().init_gl()
        print('initializing plane material')
        self.render_mode_index = GL.glGetUniformLocation(self.shader, 'render_mode')


class PlaneHorizonLineMaterial(PlaneMaterial):
    def __init__(self):
        super().__init__()
        self.render_mode = self.RenderMode.SOLID
        self.line_width = 2
        self.color = numpy.array([1, 1, 1], dtype=numpy.float32)

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        GL.glLineWidth(self.line_width)

    def create_geometry_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'plane_horizon_line.geom'), ],
            GL.GL_GEOMETRY_SHADER)
