import numpy
from OpenGL import GL
from OpenGL.arrays import vbo

from wiggle.geometry.mesh import CubeMesh
from wiggle.render.base_actor import BaseActor
from wiggle.render.base import AutoInitRenderer, VaoRenderer
from wiggle.material.wireframe import WireframeMaterial
from wiggle.material.normal import NormalMaterial


class MeshIndexBuffer(AutoInitRenderer):
    def __init__(self, mesh, primitive_type):
        super().__init__()
        self.mesh = mesh
        self.primitive_type = primitive_type
        self.out_primitive_type = primitive_type
        self.ibo = None
        self.index_type_gl = GL.GL_UNSIGNED_SHORT
        self.index_type_numpy = numpy.uint16
        self.primitive_count = 0

    def init_gl(self):
        super().init_gl()
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
        self.ibo = vbo.VBO(index_array, target=GL.GL_ELEMENT_ARRAY_BUFFER)

    def display_gl(self, *args, **kwargs):
        super().display_gl(*args, **kwargs)
        self.ibo.bind()
        GL.glDrawElements(self.out_primitive_type, self.primitive_count, self.index_type_gl, None)

    def dispose_gl(self):
        if self.ibo is not None:
            self.ibo.delete()
            self.ibo = None
        super().dispose_gl()


class MeshVbo(AutoInitRenderer, VaoRenderer):
    def __init__(self, mesh):
        super().__init__()
        self.mesh = mesh
        self.vbo = None
        self.ibos = dict()
        self._primitive = None

    def init_gl(self):
        super().init_gl()
        vpos_location = 0  # todo: less hard coded please
        vertex_array = numpy.array(self.mesh.vertexes, dtype=numpy.float32)
        self.vbo = vbo.VBO(vertex_array)
        GL.glEnableVertexAttribArray(vpos_location)
        self.vbo.bind()
        GL.glVertexAttribPointer(vpos_location, 3, GL.GL_FLOAT, False, 0, self.vbo)

    def display_gl(self, camera, *args, **kwargs):
        if self._primitive is None:
            raise ValueError()
        super().display_gl(camera=camera, *args, **kwargs)
        self.vbo.bind()
        if self._primitive not in self.ibos:
            self.ibos[self._primitive] = MeshIndexBuffer(self.mesh, self._primitive)
        ibo = self.ibos[self._primitive]
        ibo.display_gl(camera=camera, *args, **kwargs)

    def dispose_gl(self):
        if self.vbo is not None:
            self.vbo.delete()
            self.vbo = None
        for i in self.ibos.values():
            i.dispose_gl()
        self.ibos.clear()
        super().dispose_gl()

    @property
    def primitive(self):
        return self._primitive

    @primitive.setter
    def primitive(self, primitive):
        self._primitive = primitive


class MeshActor(BaseActor):
    def __init__(self, mesh=CubeMesh(), material=NormalMaterial(), wireframe_material=WireframeMaterial(), *args, **kwargs):
        """
        :type mesh: BaseMesh
        :type material: BaseMaterial
        :type wireframe_material: BaseMaterial
        """
        super().__init__(*args, **kwargs)
        self.material = material
        self.wireframe_material = wireframe_material
        self.mesh_vbo = MeshVbo(mesh)
        self.wireframe = False

    def init_gl(self):
        super().init_gl()
        self.mesh_vbo.init_gl()

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera=camera, *args, **kwargs)
        mat = self.wireframe_material if self.wireframe else self.material
        mat.display_gl(camera, *args, **kwargs)
        for name, location in mat.mvp_matrices.items():
            if name == 'projection':
                GL.glUniformMatrix4fv(location, 1, True, camera.projection)
            elif name == 'model':
                GL.glUniformMatrix4fv(location, 1, True, self.model_matrix.matrix)
            elif name == 'view':
                GL.glUniformMatrix4fv(location, 1, True, camera.view_matrix)
            elif name == 'model_view':
                GL.glUniformMatrix4fv(location, 1, True, (self.model_matrix @ camera.view_matrix).pack())
        self.mesh_vbo.primitive = mat.primitive()
        self.mesh_vbo.display_gl(camera=camera, *args, **kwargs)

    def dispose_gl(self):
        if self.mesh_vbo is not None:
            self.mesh_vbo.dispose_gl()
        super().dispose_gl()
