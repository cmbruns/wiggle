class ObjParseError(Exception):
    pass


class Mesh(object):
    def __init__(self, name='mesh'):
        self.name = name
        self.vertexes = []
        self.vertex_normals = []
        self.normal_for_vertex = dict()
        self.faces = []
        self.triangle_strips = []
        self._edges = []
        self.edges_need_update = True

    @property
    def edges(self):
        if self.edges_need_update:
            self._edges.clear()
            e = set()
            for f in self.faces:
                prev = f[-1]
                for i in range(len(f)):
                    v = f[i]
                    e.add(tuple(sorted((v, prev))))
                    prev = v
            self._edges.extend(sorted(e))
        return self._edges

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
        if vc > 0:
            # e.g. 'const vec3 CUBE_VERTEXES[8] = vec3[8]('
            lines.append(f'\nconst vec3 VERTEXES[{vc}] = vec3[{vc}](')
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
        if ec > 0:
            # e.g. 'const int EDGE_INDEXES[24] = int[24]('
            lines.append(f'\nconst int EDGE_INDEXES[{2*ec}] = int[{2*ec}](')
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


class ScreenQuadMesh(Mesh):
    def __init__(self, name='plane'):
        super().__init__(name)
        self.vertexes.extend((
            (-1, -1, 0.5),
            (1, -1, 0.5),
            (1, 1, 0.5),
            (-1, 1, 0.5),
        ), )
        self.faces.extend(( (0, 1, 2, 3), ), )
        self.triangle_strips.extend((0, 1, 3, 2), )


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
        self.faces.extend((
            (4, 5, 7, 6),  # near
            (1, 3, 7, 5),  # right
            (0, 4, 6, 2),  # left
            (0, 2, 3, 1),  # far
            (2, 6, 7, 3),  # top
            (0, 1, 5, 4),  # bottom
        ), )
        self.triangle_strips.extend(
            (
                (
                    2, 6, 3, 7, 5, 6, 4, 2, 0, 3, 1, 5, 0, 4
                ),
            ),
        )


def main():
    from wiggle.material.wireframe import WireframeMaterial
    c = WireframeMaterial(CubeMesh())
    print(c.vertex_shader_string())


if __name__ == '__main__':
    main()
