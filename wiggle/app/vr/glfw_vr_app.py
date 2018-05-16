# file glfw_vr_app.py

import glfw
from OpenGL import GL

from wiggle.app.vr import gl_renderer
import wiggle.render.demo


class GlfwVrApp(object):
    def __init__(self, actors=[], title="GlfwApp"):
        """Creates an OpenGL context and a window, and acquires OpenGL resources"""
        renderer = gl_renderer.OpenVrGlRenderer(actor=actors, multisample=2)

        self.renderer = renderer
        self.title = title
        self._is_initialized = False  # keep track of whether self.init_gl() has been called

        if not glfw.init():
            raise Exception("GLFW Initialization error")
        # Use modern OpenGL version 4.5 core
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 5)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        # Double buffered screen mirror stalls VR headset rendering,
        # So use single-buffering
        glfw.window_hint(glfw.DOUBLEBUFFER, False)
        self.window = glfw.create_window(self.renderer.window_size[0], self.renderer.window_size[1], self.title, None,
                                         None)
        if self.window is None:
            glfw.terminate()
            raise Exception("GLFW window creation error")
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.make_context_current(self.window)
        glfw.swap_interval(0)

    def __enter__(self):
        """setup for RAII using 'with' keyword"""
        return self

    def __exit__(self, type_arg, value, traceback):
        """cleanup for RAII using 'with' keyword"""
        self.dispose_gl()

    def init_gl(self):
        if self._is_initialized:
            return  # only initialize once
        if self.renderer:
            glfw.make_context_current(self.window)
            self.renderer.init_gl()
            self._is_initialized = True

    def render_scene(self):
        """render scene one time"""
        self.init_gl()  # should be a no-op after the first frame is rendered
        glfw.make_context_current(self.window)
        self.renderer.render_scene()
        # Done rendering
        # glfw.swap_buffers(self.window) # avoid double buffering to avoid stalling
        GL.glFlush()  # single buffering
        glfw.poll_events()

    def dispose_gl(self):
        if self.window:
            glfw.make_context_current(self.window)
            if self.renderer:
                self.renderer.dispose_gl()
        glfw.destroy_window(self.window)
        glfw.terminate()
        self._is_initialized = False

    def key_callback(self, _window, key, _scan_code, action, _mods):
        """press ESCAPE to quit the application"""
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(self.window, True)

    def run_loop(self):
        """keep rendering until the user says quit"""
        while not glfw.window_should_close(self.window):
            self.render_scene()


def main():
    import wiggle.demo
    # cube = wiggle.render.demo.wireframe_cube_demo()
    cube = wiggle.render.demo.color_cube_demo()
    renderer = wiggle.Renderer()
    renderer.add_actor(cube)
    with GlfwVrApp(actors=[renderer, ]) as app:
        app.run_loop()


if __name__ == '__main__':
    main()
