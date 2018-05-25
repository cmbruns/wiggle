import wiggle
from wiggle.geometry.mesh import ScreenQuadMesh
from wiggle.render.mesh_actor import MeshActor
from wiggle.material.nothing import NothingMaterial
from wiggle.material.skysphere import SkySphereMaterial


class SkySphereActor(MeshActor):
    def __init__(self):
        super().__init__(
            mesh=ScreenQuadMesh(),  # todo: finite proxy geometry
            material=SkySphereMaterial(),
            wireframe_material=NothingMaterial(),
            render_pass=wiggle.render.base.RenderPassType.OPAQUE,
        )
