import sys
import textwrap
import pkg_resources
import re

from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader

from wiggle import AutoInitRenderer
from wiggle.geometry.mesh import CubeMesh


def _ss(string):
    return textwrap.dedent(string)


class ShaderStage(object):
    def __init__(self, blocks, stage=GL.GL_FRAGMENT_SHADER):
        super().__init__()
        self.blocks = blocks
        self.gl_stage = stage
        self._index_blocks()

    def __str__(self):
        result = []
        for b in self.blocks:
            result.append(str(b))
        return '\n'.join(result)

    def _index_blocks(self):
        self._next_block_index = 0
        self.file_name_for_block_index = dict()
        self.index_for_block_file_name = dict()
        for b in self.blocks:
            file_name = b.info.full_file_name()
            if file_name not in self.index_for_block_file_name:
                index = self._next_block_index
                self._next_block_index += 1
                self.file_name_for_block_index[index] = file_name
                self.index_for_block_file_name[file_name] = index

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
                file_index = int(match.group(1))
                file_name = self.file_name_for_block_index[file_index]
                lines.append(f'  File "{file_name}", line {line_number}, in GLSL shader program')
            else:
                lines.append(line)
        if len(lines) < 1:
            return ''
        return '\n'.join(lines)

    def compile(self):
        try:
            result = compileShader(str(self), self.gl_stage)
            do_warn = True
            if do_warn:
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
            else:
                raise


class ShaderBlockInfo(object):
    def __init__(self, package, file_name):
        self.package = package
        self.file_name = file_name
        self.line_count = 0

    def full_file_name(self):
        return pkg_resources.resource_filename(self.package, self.file_name)


class ShaderFileBlock(object):
    def __init__(self, package, file_name):
        self.info = ShaderBlockInfo(package, file_name)
        self.lines = []

    def __str__(self):
        result = []
        self.load()
        for line in self.lines:
            result.append(str(line))
        return '\n'.join(result)

    def load(self):
        self.lines.clear()
        line_index = 0
        for line in pkg_resources.resource_stream(self.info.package, self.info.file_name):
            line_index += 1
            self.lines.append(ShaderLine(line=line.decode(), block_info=self.info, block_line_index=line_index))


class ShaderLine(object):
    def __init__(self, line, block_info, block_line_index, shader_line_index=None):
        self.string = line
        self.block_info = block_info
        self.block_line_index = block_line_index
        self.shader_line_index = shader_line_index

    def __str__(self):
        return self.string


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
        return ShaderStage([ShaderFileBlock('wiggle.glsl', 'white_color.frag'), ], GL.GL_FRAGMENT_SHADER)

    def init_gl(self):
        super().init_gl()
        self.shader = compileProgram(
            self.vertex_shader_string().compile(),
            self.fragment_shader_string().compile(),
        )

    def vertex_shader_string(self):
        return ShaderStage([ShaderFileBlock('wiggle.glsl', 'wireframe_cube.vert'), ],  GL.GL_VERTEX_SHADER)

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        GL.glLineWidth(3)
        GL.glDrawArrays(GL.GL_LINES, 0, 24)


def main():
    c = WireframeMaterial(CubeMesh())
    print(c.vertex_shader_string())


if __name__ == '__main__':
    main()
