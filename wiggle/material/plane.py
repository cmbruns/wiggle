from enum import Enum

import pkg_resources
from OpenGL import GL
from OpenGL.raw.GL.EXT.texture_filter_anisotropic import GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT, \
    GL_TEXTURE_MAX_ANISOTROPY_EXT
from PIL import Image

import numpy

from wiggle.material import BaseMaterial
from wiggle.material.shader import ShaderStage, ShaderFileBlock


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

    def __init__(self):
        super().__init__()
        self.render_mode_index = None
        self.render_mode = self.RenderMode.TEXTURE
        img_stream = pkg_resources.resource_stream('wiggle.images', 'uv_test.png')
        self.test_image = Image.open(img_stream, 'r')
        self.texture_id = None

    def create_vertex_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'plane.vert'), ],
            GL.GL_VERTEX_SHADER)

    def create_fragment_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'plane.frag'), ],
            GL.GL_FRAGMENT_SHADER)

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        GL.glEnable(GL.GL_CLIP_PLANE0)
        #
        GL.glUniform1i(self.render_mode_index, self.render_mode.value)
        if self.render_mode == self.RenderMode.TEXTURE:
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)

    def init_gl(self):
        super().init_gl()
        print('initializing plane material')
        self.render_mode_index = GL.glGetUniformLocation(self.shader, 'render_mode')
        # todo: move texture stuff to a texture class
        self.texture_id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,  # level-of-detail
            GL.GL_RGB,  # internal format
            self.test_image.size[0],  # width
            self.test_image.size[1],  # height
            0,  # border, must be zero
            GL.GL_RGB,  # format
            GL.GL_UNSIGNED_BYTE,  # type
            self.test_image.tobytes('raw', 'RGB', 0, -1)
        )
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_LINEAR)
        fLargest = GL.glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, fLargest)
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)


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
