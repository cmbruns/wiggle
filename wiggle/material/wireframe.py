import sys
import textwrap
import pkg_resources
import re

from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader

from wiggle import AutoInitRenderer
from wiggle.geometry.mesh import CubeMesh




# todo: separate classes for string-from-one-file vs. final string with version and #line entries etc.
class FullShaderFromFile(object):
    def __init__(self, shader_type, package, file_name, ):
        super().__init__()
        self.shader_type = shader_type
        s = ''
        line_index = 0
        for line in pkg_resources.resource_stream(package, file_name):
            line_index += 1
            s += line.decode()
        self._string = s
        self.file_name = pkg_resources.resource_filename(package, file_name)
        print(self.file_name)

    def compile(self):
        try:
            result = compileShader(self._string, self.shader_type)
        except RuntimeError as error:
            ei = sys.exc_info()
            msg = ei[1]
            # Shader compile failure (0): b'0(34) : warning C7022: unrecognized profile specifier "bork"\n0(34) : error C7558: OpenGL does not allow profile specifiers on declarations\n'
            error_message = msg.args[0]
            new_message = list()
            m = re.match(r'^(Shader compile failure \(\d+\):) b\'(.*)\'', error_message)
            if m:
                new_message.append(f' {m.group(1)}')
                for item in m.group(2).split(r'\n'):
                    # 0(34) : warning C7022: unrecognized profile specifier "bork"
                    # Poorly escaped quotes here:
                    # 0(34) : error C0000: syntax error, unexpected identifier, expecting \',\' or \';\' at token "vertexIndex"
                    item = item.replace(r"\'", "'")
                    item = item.strip()
                    if len(item) < 1:
                        continue
                    new_message.append(f'    {item}')
                    m2 = re.match(r'(\d+)\((\d+)\) : .*', item)
                    if m2:
                        line = m2.group(2)
                        file_index = m2.group(1)
                        new_message.append(f'  File "{self.file_name}", line {line}, in GLSL shader program')
            raise SyntaxError('\n'.join(new_message)) from error
        return result


def _ss(string):
    return textwrap.dedent(string)


class WireframeMaterial(AutoInitRenderer):
    # todo: eliminate mesh from shader, so different meshes can be shown with the same material
    def __init__(self, static_mesh=None):
        super().__init__()
        if static_mesh is not None:
            self._static_mesh_string = _ss(static_mesh.glsl_geometry())
            self._edge_count = len(static_mesh.edges)
        else:
            self._static_mesh_string = None
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
            self.vertex_shader_string().compile(),
            compileShader(self.fragment_shader_string(), GL.GL_FRAGMENT_SHADER),
        )

    def vertex_shader_string(self):
        return FullShaderFromFile(GL.GL_VERTEX_SHADER, 'wiggle.glsl', 'wireframe_cube.vert')
        s = ''
        line_index = 0
        for line in pkg_resources.resource_stream('wiggle.glsl', 'wireframe_cube.vert'):
            line_index += 1
            s += line.decode()
        return s

    def vertex_shader_string0(self):
        s = ''
        s += _ss('#version 430\n')
        s += _ss("""
            layout(location = 0) uniform mat4 Projection = mat4(1);
            layout(location = 4) uniform mat4 ModelView = mat4(1);
        """)
        if self._static_mesh_string is None:
            s += _ss("""
                in vec3 position;
            
                void main() {
            """)
        else:
            s += self._static_mesh_string
            s += _ss("""
                void main() {
                  int vertexIndex = EDGE_INDEXES[gl_VertexID];
                  vec3 position = VERTEXES[vertexIndex];
            """)
        s += _ss("""
                  gl_Position = Projection * ModelView * vec4(position, 1.0);
                }
        """)
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
