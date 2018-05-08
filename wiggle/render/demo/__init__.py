import wiggle
from wiggle.geometry.mesh import MeshActor


def color_cube_demo():
    cube = wiggle.ColorCubeActor()
    cube.model_center = (0, 1.2, 0)
    cube.scale = 0.3
    return cube


def wireframe_cube_demo():
    # cube = wiggle.WireframeCubeActor()
    cube = MeshActor()
    cube.model_center = (0, 1.2, 0)
    cube.scale = 0.3
    return cube
