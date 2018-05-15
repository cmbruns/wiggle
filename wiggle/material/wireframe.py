from OpenGL import GL

from wiggle import AutoInitRenderer

from wiggle.material.shader import CompositeShaderStage, ShaderFileBlock, ShaderProgram, ShaderStage


class BaseMaterial(AutoInitRenderer):
    # todo: eliminate mesh from shader, so different meshes can be shown with the same material
    def __init__(self, static_mesh=None):
        super().__init__()
        if static_mesh is not None:
            self._static_mesh_string = (static_mesh.glsl_geometry())
            self._edge_count = len(static_mesh.edges)
        else:
            self._static_mesh_string = None
        self.shader = None

    def create_vertex_shader(self):
        return None

    def create_fragment_shader(self):
        return None

    def create_geometry_shader(self):
        return None

    def has_static_mesh(self):
        return self._static_mesh_string is not None

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
    @staticmethod
    def create_fragment_shader():
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'white_color.frag'), ],
            GL.GL_FRAGMENT_SHADER)

    def create_vertex_shader(self):
        if self.has_static_mesh():
            return CompositeShaderStage(
                declarations=[
                    ShaderFileBlock('wiggle.glsl', 'model_and_view_decl.vert'),
                    ShaderFileBlock('wiggle.glsl', 'static_cube_decl.vert'),
                ],
                executions=[
                    ShaderFileBlock('wiggle.glsl', 'static_cube_edge_exec.vert'),
                    ShaderFileBlock('wiggle.glsl', 'model_and_view_exec.vert2'),
                ],
                stage=GL.GL_VERTEX_SHADER)
        else:
            return ShaderStage(
                [ShaderFileBlock('wiggle.glsl', 'positions0.vert'), ],
                GL.GL_VERTEX_SHADER)

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        GL.glLineWidth(3)

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
