import wiggle
import wiggle.render.demo
from wiggle.app.vr.glfw_vr_app import GlfwVrApp
from wiggle.render.mesh_actor import PlaneActor


def main():
    # cube = wiggle.render.demo.wireframe_cube_demo()
    cube = wiggle.render.demo.color_cube_demo()
    renderer = wiggle.Renderer()
    renderer.add_actor(cube)
    renderer.add_actor(PlaneActor())
    with GlfwVrApp(actors=[renderer, ]) as app:
        app.run_loop()


if __name__ == '__main__':
    main()
