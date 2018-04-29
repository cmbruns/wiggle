from OpenGL import GL

from .base import AbstractRenderable, BaseRenderer


class ScreenClearer(AbstractRenderable):
    """Initializes the display to a solid color, and clears depth buffer"""
    def __init__(self, red=0.5, green=0.5, blue=0.5, alpha=1.0):
        self.red = float(red)
        self.green = float(green)
        self.blue = float(blue)
        self.alpha = float(alpha)
        self.clear_mask = GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT

    def display_gl(self, *args, **kwargs):
        GL.glClearColor(self.red, self.green, self.blue, self.alpha)
        GL.glClear(self.clear_mask)


class RenderPass(BaseRenderer):
    def __init__(self, order):
        super().__init__()
        self.order = order  # lower numbered passes are rendered before higher numbered ones


class SkyPass(RenderPass):
    def __init__(self):
        super().__init__(100)
        # Default sky box is solid gray
        self.children.append(ScreenClearer())


class OpaquePass(RenderPass):
    def __init__(self):
        super().__init__(400)


class Renderer(BaseRenderer):
    """Organizes render passes and creates a default VBO"""
    def __init__(self):
        super().__init__()
        self.sky_pass = SkyPass()
        self.opaque_pass = OpaquePass()
        self._inactive_passes = [self.opaque_pass]
        self.children.clear()
        self.children.append(self.sky_pass)
        self._active_passes = self.children
