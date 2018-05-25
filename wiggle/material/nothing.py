from wiggle.material import BaseMaterial


class NothingMaterial(BaseMaterial):
    def display_gl(self, camera, *args, **kwargs):
        pass