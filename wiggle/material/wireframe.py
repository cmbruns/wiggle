from OpenGL import GL

from wiggle.material import BaseMaterial
from wiggle.material.shader import ShaderFileBlock, ShaderStage


class WireframeMaterial(BaseMaterial):
    def __init__(self):
        super().__init__()
        self.line_width = 2

    def create_fragment_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'color.frag'), ],
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

    def primitive(self):
        return GL.GL_LINES


def main():
    print(WireframeMaterial.create_vertex_shader())


if __name__ == '__main__':
    main()
