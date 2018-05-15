import sys
import pkg_resources
import re

from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL import GL


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

    def _index_one_block(self, block):
        file_name = block.info.full_file_name()
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


class ShaderStage(BaseShaderStage):
    def __init__(self, blocks, stage=GL.GL_FRAGMENT_SHADER):
        super().__init__(stage=stage)
        self.blocks = blocks
        self._index_blocks()

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

    def _index_blocks(self):
        for block in self.blocks:
            self._index_one_block(block)


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

