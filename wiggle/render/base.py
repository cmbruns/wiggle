from collections import deque
import enum

from OpenGL import GL


class RenderPassType(enum.Enum):
    """
    Lower numbered passes are rendered before higher numbered ones.
    """
    CLEAR = 100  # Just clears the screen
    SKY = 200  # At infinity, no depth buffer, painter's algorithm
    GROUND = 300  # Mixture of infinity and nearby, depth buffer + painter's algorithm
    OPAQUE = 400  # Depth buffer, first-to-paint wins (opposite to painter's)


class AbstractRenderable(object):
    def __init__(self, render_pass=RenderPassType.OPAQUE, *args, **kwargs):
        self.default_render_pass = render_pass

    """Contains stub methods for OpenGL rendering"""
    def init_gl(self):
        pass

    def display_gl(self, *args, **kwargs):
        pass

    def dispose_gl(self):
        pass


class AutoInitRenderer(AbstractRenderable):
    """Manages auto-gl_init-ialization of a static renderable"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_initialized = False

    def init_gl(self):
        self.dispose_gl()
        super().init_gl()
        self.is_initialized = True

    def display_gl(self, *args, **kwargs):
        if not self.is_initialized:
            self.init_gl()
            self.is_initialized = True
        super().display_gl(*args, **kwargs)

    def dispose_gl(self):
        super().dispose_gl()
        self.is_initialized = False


class ParentRenderer(AbstractRenderable):
    """Manages children of a container renderable"""
    def __init__(self):
        super().__init__()
        self.children = list()

    def display_gl(self, *args, **kwargs):
        super().display_gl(*args, **kwargs)
        for c in self.children:
            c.display_gl(*args, **kwargs)

    def dispose_gl(self):
        for c in self.children:
            c.dispose_gl()
        super().dispose_gl()


class VaoRenderer(AbstractRenderable):
    """Create a default VBO"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vao = None

    def init_gl(self):
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        super().init_gl()

    def display_gl(self, *args, **kwargs):
        GL.glBindVertexArray(self.vao)
        super().display_gl(*args, **kwargs)

    def dispose_gl(self):
        super().dispose_gl()
        if self.vao is not None:
            GL.glDeleteVertexArrays(1, (self.vao,))
        self.vao = None

