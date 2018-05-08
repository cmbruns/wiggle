from wiggle.geometry.mesh import CubeMesh
from wiggle.render.base_actor import BaseActor
from wiggle.material.wireframe import WireframeMaterial


class MeshActor(BaseActor):
    def __init__(self, mesh=CubeMesh()):
        super().__init__()
        self.material = None
        self.mesh = mesh
        self._shader = 0  # todo: delegate shader storage completely to material

    def display_gl(self, camera, *args, **kwargs):
        if self.material is None:
            self.material = WireframeMaterial(self.mesh)
            self.material.init_gl()
            # self.shader = self.material.shader
        super().display_gl(camera, *args, **kwargs)
        self.material.display_gl(camera, *args, **kwargs)

    def dispose_gl(self):
        if self.material is not None:
            self.material.dispose_gl()
            self.material = None
        super().dispose_gl()

    @property
    def shader(self):
        if self.material is not None:
            return self.material.shader
        return self._shader

    @shader.setter
    def shader(self, shader):
        # Unused, we delegate to the renderer
        self._shader = shader