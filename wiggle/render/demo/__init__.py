import wiggle
from wiggle.render.mesh_actor import MeshActor
from wiggle.geometry.mesh import CubeMesh
from wiggle.material.wireframe import WireframeMaterial
from wiggle.material.normal import NormalMaterial


def color_cube_demo():
    cube_mesh = CubeMesh()
    cube = MeshActor(mesh=cube_mesh, material=NormalMaterial())
    # cube = wiggle.ColorCubeActor()
    cube.model_center = (0, 1.2, 0)
    cube.scale = 0.3
    return cube


def wireframe_cube_demo():
    cube = CubeMesh()
    # actor = MeshActor(mesh=cube, material=WireframeMaterial(static_mesh=cube))
    actor = MeshActor(mesh=cube, material=WireframeMaterial())
    actor.model_center = (0, 1.2, 0)
    actor.scale = 0.3
    return actor
