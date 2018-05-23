from math import radians

from wiggle.render.mesh_actor import MeshActor
from wiggle.render.plane_actor import PlaneActor
from wiggle.geometry.mesh import CubeMesh
from wiggle.material.normal import NormalMaterial
from wiggle.geometry.matrix import Matrix4f
from wiggle.render.skybox_actor import SkyBoxActor


def load_test_scene(renderer):
    plane = PlaneActor()
    plane.model_center = (0, 0, 0)
    plane.model_rotation = Matrix4f.rotation(axis=(0, 1, 0), radians=radians(0))
    plane.model_scale = 1.0
    renderer.add_actor(plane)
    #
    cube = MeshActor(mesh=CubeMesh(), material=NormalMaterial())
    cube.model_center = (0, 1.2, 0)
    cube.model_scale = 0.3
    renderer.add_actor(cube)
    #
    sky_box = SkyBoxActor()
    renderer.add_actor(sky_box)
