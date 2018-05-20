from OpenGL import GL

from wiggle.render.base import AbstractRenderable, AutoInitRenderer, ParentRenderer, VaoRenderer


class ScreenClearer(AbstractRenderable):
    """Initializes the display to a solid color, and clears depth buffer"""
    def __init__(self, red=0.7, green=0.7, blue=0.7, alpha=1.0):
        self.red = float(red)
        self.green = float(green)
        self.blue = float(blue)
        self.alpha = float(alpha)
        self.clear_mask = GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT

    def display_gl(self, *args, **kwargs):
        GL.glClearColor(self.red, self.green, self.blue, self.alpha)
        GL.glClear(self.clear_mask)


class RenderPass(AutoInitRenderer, ParentRenderer):
    def __init__(self, order):
        super().__init__()
        self.order = order  # lower numbered passes are rendered before higher numbered ones
        self._is_wireframe = False

    @property
    def wireframe(self):
        return self._is_wireframe

    @wireframe.setter
    def wireframe(self, wireframe):
        for item in self.children:
            item.wireframe = wireframe
        self._is_wireframe = wireframe


class SkyPass(RenderPass):
    def __init__(self):
        super().__init__(100)
        # Default sky box is solid gray
        self.children.append(ScreenClearer())

    def display_gl(self, *args, **kwargs):
        # The sky has no finite depth
        GL.glDisable(GL.GL_DEPTH_TEST)  # todo: unless we render sky last?
        GL.glDepthMask(False)
        super().display_gl(*args, **kwargs)


class OpaquePass(RenderPass):
    def __init__(self):
        super().__init__(400)

    def display_gl(self, *args, **kwargs):
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthMask(True)
        super().display_gl(*args, **kwargs)


class Renderer(AutoInitRenderer, VaoRenderer, ParentRenderer):
    """Organizes render passes and creates a default VBO"""
    def __init__(self):
        super().__init__()
        self.sky_pass = SkyPass()
        self.opaque_pass = OpaquePass()
        self.children.clear()
        self.children.append(self.sky_pass)
        self._is_wireframe = False

    def add_actor(self, actor):
        pass_ = self.opaque_pass
        pass_.children.append(actor)
        if pass_ not in self.children:
            self.children.append(pass_)

    @property
    def wireframe(self):
        return self._is_wireframe

    @wireframe.setter
    def wireframe(self, wireframe):
        self._is_wireframe = wireframe
        self.opaque_pass.wireframe = wireframe
