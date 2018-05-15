import numpy
from OpenGL import GL
from OpenGL.arrays import vbo

from wiggle.geometry.mesh import CubeMesh
from wiggle.render.base_actor import BaseActor
from wiggle.material.wireframe import WireframeMaterial


class MeshVbo(object):
    pass


class MeshActor(BaseActor):
    def __init__(self, mesh=CubeMesh(), material=WireframeMaterial()):
        super().__init__()
        self.material = material
        self.mesh = mesh
        self.vao = None
        self.vbo = None
        self.ibo = None

    def init_gl(self):
        super().init_gl()
        self.material.init_gl()
        if not self.material.has_static_mesh():
            self.vao = GL.glGenVertexArrays(1)
            GL.glBindVertexArray(self.vao)
            vpos_location = 0  # todo: less hard coded please
            vertex_array = numpy.array(self.mesh.vertexes, dtype=numpy.float32)
            self.vbo = vbo.VBO(vertex_array)
            index_array = numpy.array(self.mesh.edges, dtype=numpy.uint16)
            self.ibo = vbo.VBO(index_array.flatten(), target=GL.GL_ELEMENT_ARRAY_BUFFER)
            self.ibo.bind()
            self.vbo.bind()
            GL.glEnableVertexAttribArray(vpos_location)
            GL.glVertexAttribPointer(vpos_location, 3, GL.GL_FLOAT, False, 0, self.vbo)

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        self.material.display_gl(camera, *args, **kwargs)
        if self.material.has_static_mesh():
            GL.glDrawArrays(self.material.primitive(), 0, 24)
        else:
            GL.glBindVertexArray(self.vao)
            self.ibo.bind()
            self.vbo.bind()
            GL.glDrawElements(self.material.primitive(), 24, GL.GL_UNSIGNED_SHORT, None)

    def dispose_gl(self):
        if self.material is not None:
            self.material.dispose_gl()
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

    @property
    def shader(self):
        return self.material.shader
