from OpenGL import GL

from wiggle import AutoInitRenderer
from wiggle.material.shader import ShaderProgram


class BaseMaterial(AutoInitRenderer):
    def __init__(self):
        super().__init__()
        self.shader = None
        self.mvp_matrices = dict()

    def _configure_depth(self):
        # standard parameters to possibly override in base classes
        GL.glDepthFunc(GL.GL_LESS)
        GL.glDepthRange(0, 1)

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

    def display_gl(self, *args, **kwargs):
        self._configure_depth()
        super().display_gl(*args, **kwargs)
        GL.glUseProgram(self.shader)

    def primitive(self):
        return GL.GL_TRIANGLES