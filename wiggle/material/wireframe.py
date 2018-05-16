from OpenGL import GL

from wiggle import AutoInitRenderer

from wiggle.material.shader import ShaderFileBlock, ShaderProgram, ShaderStage


class BaseMaterial(AutoInitRenderer):
    def __init__(self):
        super().__init__()
        self.shader = None

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


class WireframeMaterial(BaseMaterial):
    def __init__(self):
        super().__init__()
        self.line_width = 3

    @staticmethod
    def create_fragment_shader():
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
            GL.GL_FRAGMENT_SHADER)

    def create_geometry_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'per_face_normals.geom'), ],
            GL.GL_FRAGMENT_SHADER)

    def create_fragment_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'white_color.frag'), ],
            GL.GL_FRAGMENT_SHADER)

    @staticmethod
    def primitive():
        return GL.GL_TRIANGLES


def main():
    print(WireframeMaterial.create_vertex_shader())


if __name__ == '__main__':
    main()
