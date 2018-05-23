from OpenGL import GL

from wiggle.render.base import AbstractRenderable, AutoInitRenderer, ParentRenderer, VaoRenderer, RenderPassType


class ScreenClearer(AbstractRenderable):
    """Initializes the display to a solid color, and clears depth buffer"""
    def __init__(self, red=0.7, green=0.7, blue=0.7, alpha=1.0):
        super().__init__(render_pass=RenderPassType.SKY)
        self.red = float(red)
        self.green = float(green)
        self.blue = float(blue)
        self.alpha = float(alpha)
        self.clear_mask = GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT

    def display_gl(self, *args, **kwargs):
        GL.glClearColor(self.red, self.green, self.blue, self.alpha)
        GL.glClear(self.clear_mask)


class RenderPass(AutoInitRenderer, ParentRenderer):
    def __init__(self, pass_type):
        """

        :type pass_type: RenderPassType
        """
        super().__init__()
        self.pass_type = pass_type
        self._is_wireframe = False

    def __eq__(self, other):
        return self.pass_type.value == other.pass_type.value

    def __ne__(self, other):
        return self.pass_type.value != other.pass_type.value

    def __lt__(self, other):
        return self.pass_type.value < other.pass_type.value

    def __le__(self, other):
        return self.pass_type.value <= other.pass_type.value

    def __gt__(self, other):
        return self.pass_type.value > other.pass_type.value

    def __ge__(self, other):
        return self.pass_type.value >= other.pass_type.value

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
        super().__init__(RenderPassType.SKY)
        # Default sky box is solid gray
        self.children.append(ScreenClearer())

    def display_gl(self, *args, **kwargs):
        # The sky has no finite depth
        GL.glDisable(GL.GL_DEPTH_TEST)  # Last to paint anywhere wins
        GL.glDepthMask(False)
        super().display_gl(*args, **kwargs)


class GroundPass(RenderPass):
    def __init__(self):
        super().__init__(RenderPassType.GROUND)

    def display_gl(self, *args, **kwargs):
        # The sky has no finite depth
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthMask(True)
        GL.glDepthFunc(GL.GL_LEQUAL)  # Paint over existing background, even at infinity.
        super().display_gl(*args, **kwargs)


class OpaquePass(RenderPass):
    def __init__(self):
        super().__init__(RenderPassType.OPAQUE)

    def display_gl(self, *args, **kwargs):
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthMask(True)
        GL.glDepthFunc(GL.GL_LESS)  # First to paint at a particular depth wins
        super().display_gl(*args, **kwargs)


class Renderer(AutoInitRenderer, VaoRenderer, ParentRenderer):
    """Organizes render passes and creates a default VBO"""
    def __init__(self):
        super().__init__()
        self.sky_pass = SkyPass()
        self.ground_pass = GroundPass()
        self.opaque_pass = OpaquePass()
        self.children.clear()
        self.children.append(self.sky_pass)
        self._is_wireframe = False

    def add_actor(self, actor):
        pass_switcher = {
            RenderPassType.SKY: self.sky_pass,
            RenderPassType.GROUND: self.ground_pass,
            RenderPassType.OPAQUE: self.opaque_pass,
        }
        pass_ = pass_switcher.get(actor.default_render_pass, self.opaque_pass)
        pass_.children.append(actor)
        if pass_ not in self.children:
            self.children.append(pass_)
            self.children[:] = sorted(self.children[:])

    @property
    def wireframe(self):
        return self._is_wireframe

    @wireframe.setter
    def wireframe(self, wireframe):
        self._is_wireframe = wireframe
        for pass_ in self.children:
            pass_.wireframe = wireframe
