import numpy
from OpenGL import GL

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


class PlaneMaterial(BaseMaterial):
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
        GL.glDepthRange(1, 1)  # Draw skybox at infinity...
        GL.glDepthFunc(GL.GL_LEQUAL)  # ...but paint over other infinitely distant things, such as the result of glClear
        GL.glEnable(GL.GL_CLIP_PLANE0)

    @staticmethod
    def primitive():
        return GL.GL_TRIANGLES


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
