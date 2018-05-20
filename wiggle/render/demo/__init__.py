from wiggle.render.mesh_actor import MeshActor, PlaneActor
from wiggle.geometry.mesh import CubeMesh
from wiggle.material.wireframe import WireframeMaterial
from wiggle.material.normal import NormalMaterial


def load_test_scene(renderer):
    plane = PlaneActor()
    plane.model_center = (1, 1, 1)
    renderer.add_actor(plane)
    cube = MeshActor(mesh=CubeMesh(), material=NormalMaterial())
    cube.model_center = (0, 1.2, 0)
    cube.scale = 0.3
    renderer.add_actor(cube)


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
