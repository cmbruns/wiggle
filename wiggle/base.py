from OpenGL import GL


class AbstractRenderable(object):
    """Contains stub methods for OpenGL rendering"""
    def init_gl(self):
        pass

    def display_gl(self, *args, **kwargs):
        pass

    def dispose_gl(self):
        pass


class AutoInitRenderer(AbstractRenderable):
    """Manages auto-gl_init-ialization of a static renderable"""
    def __init__(self):
        super().__init__()
        self.is_initialized = False

    def init_gl(self):
        super().init_gl()
        self.is_initialized = True

    def display_gl(self, *args, **kwargs):
        if not self.is_initialized:
            super().init_gl()
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
    def __init__(self):
        super().__init__()
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

