from OpenGL import GL

from wiggle.material import BaseMaterial
from wiggle.material.shader import ShaderStage, ShaderFileBlock


class NormalMaterial(BaseMaterial):
    def create_vertex_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'untransformed.vert'), ],
            GL.GL_VERTEX_SHADER)

    def create_geometry_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'per_face_normals.geom'), ],
            GL.GL_GEOMETRY_SHADER)

    def create_fragment_shader(self):
        return ShaderStage(
            [ShaderFileBlock('wiggle.glsl', 'normal_color.frag'), ],
            GL.GL_FRAGMENT_SHADER)

    @staticmethod
    def primitive():
        return GL.GL_TRIANGLES