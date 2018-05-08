import textwrap

from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader

from wiggle import AutoInitRenderer
from wiggle.geometry.mesh import CubeMesh


def _ss(string):
    return textwrap.dedent(string)


class WireframeMaterial(AutoInitRenderer):
    # todo: eliminate mesh from shader, so different meshes can be shown with the same material
    def __init__(self, mesh=CubeMesh()):
        super().__init__()
        self.mesh = mesh
        self.shader = None

    def fragment_shader_string(self):
        return _ss("""
            #version 430
            out vec4 FragColor;

            void main() {
              FragColor = vec4(1.0, 1.0, 1.0, 1.0);
            }
        """)

    def init_gl(self):
        super().init_gl()
        self.shader = compileProgram(
            compileShader(self.vertex_shader_string(), GL.GL_VERTEX_SHADER),
            compileShader(self.fragment_shader_string(), GL.GL_FRAGMENT_SHADER),
        )

    def vertex_shader_string(self):
        s = ''
        s += _ss('#version 430\n')
        s += _ss("""
            layout(location = 0) uniform mat4 Projection = mat4(1);
            layout(location = 4) uniform mat4 ModelView = mat4(1);
        """)
        s += _ss(self.mesh.glsl_geometry())
        n = self.mesh.glsl_name()
        s += _ss("""
            void main() {
              int vertexIndex = %s_EDGE_INDEXES[gl_VertexID];
              gl_Position = Projection * ModelView * vec4(%s_VERTEXES[vertexIndex], 1.0);
            }
        """ % (n, n))
        return s

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        GL.glLineWidth(3)
        GL.glDrawArrays(GL.GL_LINES, 0, 24)


def main():
    c = WireframeMaterial(CubeMesh())
    print(c.vertex_shader_string())


if __name__ == '__main__':
    main()
