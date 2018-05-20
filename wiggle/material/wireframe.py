from enum import Enum
import pkg_resources

from PIL import Image
from OpenGL import GL
from OpenGL.GL.EXT.texture_filter_anisotropic import GL_TEXTURE_MAX_ANISOTROPY_EXT, GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT

from wiggle import AutoInitRenderer
from wiggle.material.shader import ShaderFileBlock, ShaderProgram, ShaderStage


class BaseMaterial(AutoInitRenderer):
    def __init__(self):
        super().__init__()
        self.shader = None
        self.mvp_matrices = dict()

    def _query_matrices(self):
        """Note which model, view, projection, etc. matrices are needed to run this shader"""
        num_active_uniforms = GL.glGetProgramiv(self.shader, GL.GL_ACTIVE_UNIFORMS)
        for u in range(num_active_uniforms):
            name, size, type_ = GL.glGetActiveUniform(self.shader, u)
            name = name.decode()
            if not type_ == GL.GL_FLOAT_MAT4:
                continue
            if not size == 1:
                continue
            location = GL.glGetUniformLocation(self.shader, name)
            self.mvp_matrices[name] = location

    def create_vertex_shader(self):
        return None

    def create_fragment_shader(self):
        return None

    def create_geometry_shader(self):
        return None

    def init_gl(self):
        super().init_gl()
        stages = []
        for stage in (self.create_fragment_shader(),
                      self.create_geometry_shader(),
                      self.create_vertex_shader()):
            if stage is not None:
                stages.append(stage)
        self.shader = int(ShaderProgram(stages))
        self._query_matrices()

    def primitive(self):
        return GL.GL_TRIANGLES


class PlaneMaterial(BaseMaterial):
    class RenderMode(Enum):
        """
        Synchronize these values with those in plane.frag
        """
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
        GL.glLineWidth(20)
        GL.glDepthFunc(GL.GL_LEQUAL)  # ...but paint over other infinitely distant things, such as the result of glClear
        GL.glEnable(GL.GL_CLIP_PLANE0)
        #
        GL.glUniform1i(self.render_mode_index, self.render_mode.value)
        if self.render_mode == self.RenderMode.TEXTURE:
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)

    def init_gl(self):
        super().init_gl()
        self.render_mode_index = GL.glGetUniformLocation(self.shader, 'render_mode')
        #
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

    def dispose_gl(self):
        super().dispose_gl()


class WireframeMaterial(BaseMaterial):
    def __init__(self):
        super().__init__()
        self.line_width = 3

    def create_fragment_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'white_color.frag'), ],
            GL.GL_FRAGMENT_SHADER)

    def create_vertex_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'positions0.vert'), ],
            GL.GL_VERTEX_SHADER)

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glLineWidth(self.line_width)

    @staticmethod
    def primitive():
        return GL.GL_LINES


class NormalMaterial(BaseMaterial):
    def create_vertex_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'untransformed.vert'), ],
            GL.GL_VERTEX_SHADER)

    def create_geometry_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'per_face_normals.geom'), ],
            GL.GL_GEOMETRY_SHADER)

    def create_fragment_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'normal_color.frag'), ],
            GL.GL_FRAGMENT_SHADER)

    @staticmethod
    def primitive():
        return GL.GL_TRIANGLES


def main():
    print(WireframeMaterial.create_vertex_shader())


if __name__ == '__main__':
    main()
