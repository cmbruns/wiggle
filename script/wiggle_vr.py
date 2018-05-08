import wiggle
import wiggle.render.demo
from wiggle.app.vr.glfw_vr_app import GlfwVrApp


def main():
    cube = wiggle.render.demo.wireframe_cube_demo()
    renderer = wiggle.Renderer()
    renderer.add_actor(cube)
    with GlfwVrApp(actors=[renderer, ]) as app:
        app.run_loop()


if __name__ == '__main__':
    main()
