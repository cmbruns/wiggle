import numpy
from OpenGL import GL
from OpenGL.arrays import vbo

from wiggle.geometry.mesh import CubeMesh
from wiggle.render.base_actor import BaseActor
from wiggle.render.base import AutoInitRenderer
from wiggle.material.wireframe import WireframeMaterial


class MeshVbo(AutoInitRenderer):
    def __init__(self, mesh, primitive_type):
        super().__init__()
        self.mesh = mesh
        self.primitive_type = primitive_type
        self.vao = None
        self.vbo = None
        self.ibo = None
        self.index_type_gl = GL.GL_UNSIGNED_SHORT
        self.index_type_numpy = numpy.uint16
        self.primitive_count = 0

    def init_gl(self):
        super().init_gl()
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        vpos_location = 0  # todo: less hard coded please
        vertex_array = numpy.array(self.mesh.vertexes, dtype=numpy.float32)
        self.vbo = vbo.VBO(vertex_array)
        index_array = numpy.array(self.mesh.edges, dtype=numpy.uint16).flatten()
        self.primitive_count = len(index_array)
        self.ibo = vbo.VBO(index_array, target=GL.GL_ELEMENT_ARRAY_BUFFER)
        self.ibo.bind()
        self.vbo.bind()
        GL.glEnableVertexAttribArray(vpos_location)
        GL.glVertexAttribPointer(vpos_location, 3, GL.GL_FLOAT, False, 0, self.vbo)

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera=camera, *args, **kwargs)
        GL.glBindVertexArray(self.vao)
        self.ibo.bind()
        self.vbo.bind()
        GL.glDrawElements(self.primitive_type, 24, self.index_type_gl, None)

    def dispose_gl(self):
        if self.vbo is not None:
            self.vbo.delete()
            self.vbo = None
        if self.ibo is not None:
            self.ibo.delete()
            self.ibo = None
        if self.vao is not None:
            GL.glDeleteVertexArrays(1, [self.vao, ])
            self.vao = None
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
        if self.material is not None:
            self.material.dispose_gl()
        if self.mesh_vbo is not None:
            self.mesh_vbo.dispose_gl()
        super().dispose_gl()

    @property
    def shader(self):
        return self.material.shader
