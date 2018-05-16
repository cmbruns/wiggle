import numpy
from OpenGL import GL
from OpenGL.arrays import vbo

from wiggle.geometry.mesh import CubeMesh
from wiggle.render.base_actor import BaseActor
from wiggle.render.base import AutoInitRenderer, VaoRenderer
from wiggle.material.wireframe import WireframeMaterial


class MeshVbo(AutoInitRenderer, VaoRenderer):
    def __init__(self, mesh, primitive_type):
        super().__init__()
        self.mesh = mesh
        self.primitive_type = primitive_type
        self.out_primitive_type = primitive_type
        self.vbo = None
        self.ibo = None
        self.index_type_gl = GL.GL_UNSIGNED_SHORT
        self.index_type_numpy = numpy.uint16
        self.primitive_count = 0

    def init_gl(self):
        super().init_gl()
        vpos_location = 0  # todo: less hard coded please
        vertex_array = numpy.array(self.mesh.vertexes, dtype=numpy.float32)
        self.vbo = vbo.VBO(vertex_array)
        if self.primitive_type == GL.GL_LINES:
            indexes = self.mesh.edges
        elif self.primitive_type == GL.GL_TRIANGLES:
            indexes = self.mesh.triangle_strips
            self.out_primitive_type = GL.GL_TRIANGLE_STRIP
        else:
            raise ValueError('primitive type not supported')
        self.primitive_count = len(indexes)
        index_array = numpy.array(indexes, dtype=numpy.uint16).flatten()
        self.primitive_count = len(index_array)
        GL.glEnableVertexAttribArray(vpos_location)
        self.vbo.bind()
        GL.glVertexAttribPointer(vpos_location, 3, GL.GL_FLOAT, False, 0, self.vbo)
        self.ibo = vbo.VBO(index_array, target=GL.GL_ELEMENT_ARRAY_BUFFER)

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera=camera, *args, **kwargs)
        self.vbo.bind()
        self.ibo.bind()
        GL.glDrawElements(self.out_primitive_type, self.primitive_count, self.index_type_gl, None)

    def dispose_gl(self):
        if self.vbo is not None:
            self.vbo.delete()
            self.vbo = None
        if self.ibo is not None:
            self.ibo.delete()
            self.ibo = None
        super().dispose_gl()


class MeshActor(BaseActor):
    def __init__(self, mesh=CubeMesh(), material=WireframeMaterial()):
        super().__init__()
        self.material = material
        self.mesh_vbo = MeshVbo(mesh, material.primitive())

    def init_gl(self):
        super().init_gl()
        self.material.init_gl()
        self.mesh_vbo.init_gl()

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera=camera, *args, **kwargs)
        self.material.display_gl(camera, *args, **kwargs)
        self.mesh_vbo.display_gl(camera=camera, *args, **kwargs)

    def dispose_gl(self):
        if self.mesh_vbo is not None:
            self.mesh_vbo.dispose_gl()
        super().dispose_gl()

    @property
    def shader(self):
        return self.material.shader
