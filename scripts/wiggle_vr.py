from wiggle.render.renderer import Renderer
import wiggle.render.demo
from wiggle.app.vr.glfw_vr_app import GlfwVrApp


def main():
    renderer = Renderer()
    wiggle.render.demo.load_test_scene(renderer)
    with GlfwVrApp(actors=[renderer, ]) as app:
        app.run_loop()


if __name__ == '__main__':
    main()
