import textwrap

from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram

from wiggle.actor.base_actor import BaseActor
from wiggle.renderer import AutoInitRenderer


class ObjParseError(Exception):
    pass


class Mesh(object):
    def __init__(self, name='mesh'):
        self.name = name
        self.vertexes = []
        self.vertex_normals = []
        self.normal_for_vertex = dict()
        self.faces = []
        self.edges = []

    def glsl_name(self):
        return self.name.upper()

    def _parse_obj_line(self, line):
        if line.startswith('#'):
            # e.g. "# Blender v2.65 (sub 0) OBJ File"
            return  # ignore comments
        elif line.startswith('o '):
            # e.g. "o teapot.005"
            self.name = line.split()[1]
        elif line.startswith('v '):
            # e.g. "v -0.498530 0.712498 -0.039883"
            vec3 = [float(x) for x in line.split()[1:4]]
            self.vertexes.append(vec3)
        elif line.startswith('vn '):
            # e.g. "vn -0.901883 0.415418 0.118168"
            vec3 = [float(x) for x in line.split()[1:4]]
            self.vertex_normals.append(vec3)
        elif line.startswith('s '):
            return  # ignore whatever "s" is
            # print(line)
        elif line.startswith('f '):
            face = list()
            for c in line.split()[1:]:
                v, n = [int(x) for x in c.split('/')[0:3:2]]
                face.append(v - 1)  # vertex index
                self.normal_for_vertex[v - 1] = self.vertex_normals[n - 1]
                self.faces.append(face)
        else:
            raise ObjParseError(f'unrecognized OBJ line: "{line}"')

    def glsl_geometry(self):
        """Generate a GLSL string explicitly declaring this mesh geometry"""
        return self.glsl_vertexes() + self.glsl_edges()

    def glsl_vertexes(self):
        vc = len(self.vertexes)
        if vc < 1:
            return ''
        lines = []
        name = self.glsl_name()
        if vc > 0:
            # e.g. 'const vec3 CUBE_VERTEXES[8] = vec3[8]('
            lines.append(f'\nconst vec3 {name}_VERTEXES[{vc}] = vec3[{vc}](')
            comma = ','
            for i in range(vc):
                v = self.vertexes[i]
                if i >= vc - 1:
                    comma = ''
                # e.g. 'vec3(-1, -1, -1),'
                lines.append(f'  vec3({v[0]}, {v[1]}, {v[2]}){comma}')
            lines.append(');\n')
        return '\n'.join(lines)

    def glsl_edges(self):
        ec = len(self.edges)
        if ec < 1:
            return ''
        lines = []
        name = self.glsl_name()
        if ec > 0:
            # e.g. 'const int EDGE_INDEXES[24] = int[24]('
            lines.append(f'\nconst int {name}_EDGE_INDEXES[{2*ec}] = int[{2*ec}](')
            comma = ','
            for i in range(ec):
                e = self.edges[i]
                if i >= ec - 1:
                    comma = ''
                # e.g. '  0, 1,'
                lines.append(f'  {e[0]}, {e[1]}{comma}')
            lines.append(');\n')
        return '\n'.join(lines)

    def load_obj(self, stream):
        for line in stream:
            self._parse_obj_line(line)


class CubeMesh(Mesh):
    """
       2________ 3
       /|      /|
     6/_|____7/ |
      | |_____|_|
      | /0    | /1
      |/______|/
      4       5
    """
    def __init__(self, name='cube'):
        super().__init__(name)
        r = 0.5
        self.vertexes.extend((
            (-r, -r, -r),  # 0: lower left far
            (+r, -r, -r),  # 1: lower right far
            (-r, +r, -r),  # 2: upper left far
            (+r, +r, -r),  # 3: upper right far
            (-r, -r, +r),  # 4: lower left near
            (+r, -r, +r),  # 5: lower right near
            (-r, +r, +r),  # 6: upper left near
            (+r, +r, +r),  # 7: upper right near
        ), )
        self.edges.extend((
            (0, 1),  (1, 3),  (3, 2),  (2, 0),  # far
            (4, 5),  (5, 7),  (7, 6),  (6, 4),  # near
            (2, 6),  (3, 7),  (1, 5),  (0, 4),  # between
        ), )


class MeshActor(BaseActor):
    def __init__(self, mesh=CubeMesh()):
        super().__init__()
        self.renderer = None
        self.mesh = mesh
        self._shader = 0

    def display_gl(self, camera, *args, **kwargs):
        if self.renderer is None:
            self.renderer = WireframeActor(self.mesh)
            self.renderer.init_gl()
            # self.shader = self.renderer.shader
        super().display_gl(camera, *args, **kwargs)
        self.renderer.display_gl(camera, *args, **kwargs)

    def dispose_gl(self):
        if self.renderer is not None:
            self.renderer.dispose_gl()
            self.renderer = None
        super().dispose_gl()

    @property
    def shader(self):
        if self.renderer is not None:
            return self.renderer.shader
        return self._shader

    @shader.setter
    def shader(self, shader):
        # Unused, we delegate to the renderer
        self._shader = shader


def _ss(string):
    return textwrap.dedent(string)


class WireframeActor(AutoInitRenderer):
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
    c = MeshActor()
    print(c.vertex_shader_string())


if __name__ == '__main__':
    main()
