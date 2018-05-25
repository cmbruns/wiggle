import wiggle
from wiggle.geometry.mesh import ScreenQuadMesh
from wiggle.render.mesh_actor import MeshActor
from wiggle.material.skybox import SkyBoxMaterial
from wiggle.material.nothing import NothingMaterial


class SkyBoxActor(MeshActor):
    def __init__(self):
        super().__init__(
            mesh=ScreenQuadMesh(),
            material=SkyBoxMaterial(),
            wireframe_material=NothingMaterial(),
            render_pass=wiggle.render.base.RenderPassType.SKY,
        )
