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

    def _format_warnings(self, log):
        log = log.replace(r'\n', '\n')
        log = log.replace(r"\'", "'")
        lines = list()
        for line in log.split('\n'):
            line = line.strip()
            if len(line) < 1:
                continue
            lines.append(f'    {line}')
            match = re.match(r'(\d+)\((\d+)\) : .*', line)
            if match:
                line_number = match.group(2)
                file_index = match.group(1)
                lines.append(f'  File "{self.file_name}", line {line_number}, in GLSL shader program')
        if len(lines) < 1:
            return ''
        return '\n'.join(lines)

    def compile(self):
        try:
            result = compileShader(self._string, self.shader_type)
            doWarn = True
            if doWarn:
                log = GL.glGetShaderInfoLog(result)
                if len(log) > 0:
                    print(self._format_warnings(log.decode()))
            return result
        except RuntimeError as error:
            ei = sys.exc_info()
            msg = ei[1]
            # Shader compile failure (0): b'0(34) : warning C7022: unrecognized profile specifier "bork"\n0(34) : error C7558: OpenGL does not allow profile specifiers on declarations\n'
            error_message = msg.args[0]
            new_message = list()
            m = re.match(r'^(Shader compile failure \(\d+\):) b\'(.*)\'', error_message)
            if m:
                new_message.append(f' {m.group(1)}')  # Shader compile failure (0):
                new_message.append(self._format_warnings(m.group(2)))
            raise SyntaxError('\n'.join(new_message)) from error


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
        return FullShaderFromFile(GL.GL_FRAGMENT_SHADER, 'wiggle.glsl', 'white_color.frag')

    def init_gl(self):
        super().init_gl()
        self.shader = compileProgram(
            self.vertex_shader_string().compile(),
            self.fragment_shader_string().compile(),
        )

    def vertex_shader_string(self):
        return FullShaderFromFile(GL.GL_VERTEX_SHADER, 'wiggle.glsl', 'wireframe_cube.vert')

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
