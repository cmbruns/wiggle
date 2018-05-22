import wiggle
from wiggle.geometry.mesh import ScreenQuadMesh
from wiggle.material.plane import PlaneMaterial, PlaneHorizonLineMaterial
from wiggle.render.mesh_actor import MeshActor


class PlaneActor(MeshActor):
    def __init__(self):
        super().__init__(
            mesh=ScreenQuadMesh(),
            material=PlaneMaterial(),
            wireframe_material=PlaneHorizonLineMaterial(),
            render_pass=wiggle.render.base.RenderPassType.GROUND,
        )
