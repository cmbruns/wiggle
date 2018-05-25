import pkg_resources
from OpenGL import GL
from OpenGL.raw.GL.EXT.texture_filter_anisotropic import GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT, \
    GL_TEXTURE_MAX_ANISOTROPY_EXT
from PIL import Image

from wiggle.render.base import AutoInitRenderer


class Texture(AutoInitRenderer):
    def __init__(self, package, file_name, is_equirectangular=False):
        super().__init__()
        self.texture_id = None
        self.is_equirectangular = is_equirectangular
        img_stream = pkg_resources.resource_stream(package, file_name)
        self.image = Image.open(img_stream, 'r')

    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)

    def init_gl(self):
        super().init_gl()
        print('initializing skybox material')
        self.texture_id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,  # level-of-detail
            GL.GL_RGB,  # internal format
            self.image.size[0],  # width
            self.image.size[1],  # height
            0,  # border, must be zero
            GL.GL_RGB,  # format
            GL.GL_UNSIGNED_BYTE,  # type
            self.image.tobytes('raw', 'RGB', 0, -1)
        )
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_NEAREST)
        if self.is_equirectangular:
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_MIRRORED_REPEAT)
        largest_anisotropy = GL.glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, largest_anisotropy)
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)