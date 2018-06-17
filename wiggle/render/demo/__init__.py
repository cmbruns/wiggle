from math import radians

from wiggle.render.mesh_actor import MeshActor
from wiggle.render.plane_actor import PlaneActor
from wiggle.geometry.mesh import CubeMesh
from wiggle.material.normal import NormalMaterial
from wiggle.material.texture import Texture
from wiggle.geometry.matrix import Matrix4f
from wiggle.render.skybox_actor import SkyBoxActor
from wiggle.render.skysphere_actor import SkySphereActor


def load_office_scene(renderer):
    texture = Texture(
        file_name='office_mantiuk8_15_12.jpg',
        package='wiggle.images',
        is_equirectangular=True)
    sky_box = SkyBoxActor(texture=texture)
    renderer.add_actor(sky_box)
    #
    floor = PlaneActor(texture=texture)
    floor.model_center = (0, 0, 0)
    floor.model_rotation = Matrix4f.rotation(axis=(0, 1, 0), radians=radians(20))
    # floor.model_scale = 2.0
    renderer.add_actor(floor)
    #
    ceiling = PlaneActor(texture=texture)
    ceiling.model_center = (0, 2.55, 0)
    ceiling.model_rotation = Matrix4f.rotation(axis=(1, 0, 0), radians=radians(180))
    # ceiling.model_scale = 2.0
    renderer.add_actor(ceiling)
    #
    sphere = SkySphereActor()
    # renderer.add_actor(sphere)
    #
    cube = MeshActor(mesh=CubeMesh(), material=NormalMaterial())
    cube.model_center = (0, 1.2, 0)
    cube.model_scale = 0.3
    renderer.add_actor(cube)


def load_test_scene(renderer):
    load_office_scene(renderer)


def load_valley_scene(renderer):
    texture = Texture(
        file_name='office_mantiuk8_15_12.jpg',
        package='wiggle.images',
        is_equirectangular=True)
    sky_box = SkyBoxActor(texture=texture)
    renderer.add_actor(sky_box)
    #
    floor = PlaneActor(texture=texture)
    floor.model_center = (0, 0, 0)
    floor.model_rotation = Matrix4f.rotation(axis=(0, 1, 0), radians=radians(0))
    floor.model_scale = 2.0
    renderer.add_actor(floor)
    #
    ceiling = PlaneActor(texture=texture)
    ceiling.model_center = (0, 2.5, 0)
    ceiling.model_rotation = Matrix4f.rotation(axis=(1, 0, 0), radians=radians(180))
    ceiling.model_scale = 2.0
    renderer.add_actor(ceiling)
    #
    sphere = SkySphereActor()
    # renderer.add_actor(sphere)
    #
    cube = MeshActor(mesh=CubeMesh(), material=NormalMaterial())
    cube.model_center = (0, 1.2, 0)
    cube.model_scale = 0.3
    renderer.add_actor(cube)

