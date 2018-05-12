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


class ShaderProgram(object):
    def __init__(self, stages):
        self.stages = stages
        self.handle = None

    def __int__(self):
        if not self.handle:
            self.compile()
        return self.handle

    def compile(self):
        self.handle = compileProgram(*[s.compile() for s in self.stages])
        return self.handle


class BaseShaderStage(object):
    def __init__(self, stage=GL.GL_FRAGMENT_SHADER):
        super().__init__()
        self.gl_stage = stage
        self.handle = None
        self._next_block_index = 0
        self.file_name_for_block_index = dict()
        self.index_for_block_file_name = dict()

    def __int__(self):
        if not self.handle:
            self.handle = self.compile()
        return self.handle

    def __str__(self):
        result = []
        line_index = 0
        for b in self.blocks:
            b.load()
            for line in b.lines:
                line.shader_line_index = line_index
                result.append(str(line))
                line_index += 1
        return '\n'.join(result)

    def _index_one_block(self, block):
        file_name = block.info.full_file_name()
        if file_name not in self.index_for_block_file_name:
            index = self._next_block_index
            self._next_block_index += 1
            self.file_name_for_block_index[index] = file_name
            self.index_for_block_file_name[file_name] = index

    def _index_blocks(self):
        for block in self.blocks:
            self._index_one_block(block)

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


class ShaderStage(BaseShaderStage):
    def __init__(self, blocks, stage=GL.GL_FRAGMENT_SHADER):
        super().__init__(stage=stage)
        self.blocks = blocks
        self._index_blocks()


class CompositeShaderStage(BaseShaderStage):
    def __init__(self, declarations, executions, stage=GL.GL_FRAGMENT_SHADER):
        super().__init__(stage=stage)
        self.declarations = declarations
        self.executions = executions

    def __str__(self):
        result = []
        line_index = 0  # line number for final full shader
        template_line_index = 0  # line number for template skeleton shader file
        template_block = ShaderFileBlock('wiggle.glsl', 'shader_template.glsl')
        self._index_one_block(template_block)
        template_block.load()
        for line in template_block.lines:
            sl = str(line)
            m_decl = re.match(r'\s*#pragma insert_declarations', sl)
            m_exec = re.match(r'\s*#pragma insert_procedural_code', sl)
            if m_decl:
                line_index = self._append_blocks(self.declarations, result, line_index)
            elif m_exec:
                line_index = self._append_blocks(self.executions, result, line_index, indent='    ')
            else:
                result.append(str(line))
                line_index + 1
            template_line_index += 1
            # todo #line comments
        result = '\n'.join(result)
        # print(result, file=sys.stderr)
        return result

    def _append_blocks(self, blocks, out_lines, line_index, indent=''):
        for block in blocks:
            self._index_one_block(block)
            block_line_index = 0
            block.load()
            file_index = self.index_for_block_file_name[block.info.full_file_name()]
            out_lines.append(f'{indent}#line {block_line_index+1} {file_index}')
            line_index += 1
            for block_line in block.lines:
                block_line.shader_line_index = line_index
                out_lines.append(str(block_line))
                line_index += 1
                block_line_index += 1
        return line_index


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
        self.is_loaded = False

    def __str__(self):
        result = []
        self.load()
        for line in self.lines:
            result.append(str(line))
        return '\n'.join(result)

    def load(self):
        if self.is_loaded:
            return
        self.lines.clear()
        line_index = 0
        for line in pkg_resources.resource_stream(self.info.package, self.info.file_name):
            self.lines.append(ShaderLine(line=line.decode(), block_info=self.info, block_line_index=line_index))
            line_index += 1
        self.info.line_count = len(self.lines)
        self.is_loaded = True


class ShaderLine(object):
    def __init__(self, line, block_info, block_line_index, shader_line_index=None):
        self.string = str(line).rstrip()
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

    def init_gl(self):
        super().init_gl()
        if True:
            vert = CompositeShaderStage(
                    declarations=[
                        ShaderFileBlock('wiggle.glsl', 'model_and_view_decl.vert'),
                        ShaderFileBlock('wiggle.glsl', 'static_cube_decl.vert'),
                    ],
                    executions=[
                        ShaderFileBlock('wiggle.glsl', 'static_cube_edge_exec.vert'),
                        ShaderFileBlock('wiggle.glsl', 'model_and_view_exec.vert'),
                    ],
                    stage=GL.GL_VERTEX_SHADER)
        else:
            vert = ShaderStage([ShaderFileBlock('wiggle.glsl', 'wireframe_cube.vert'), ], GL.GL_VERTEX_SHADER)
        self.shader = int(ShaderProgram([
            vert,
            ShaderStage([ShaderFileBlock('wiggle.glsl', 'white_color.frag'), ], GL.GL_FRAGMENT_SHADER),
        ]))

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        GL.glLineWidth(3)
        GL.glDrawArrays(GL.GL_LINES, 0, 24)


def main():
    c = WireframeMaterial(CubeMesh())
    print(c.vertex_shader())


if __name__ == '__main__':
    main()
