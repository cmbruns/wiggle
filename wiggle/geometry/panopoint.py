from wiggle.geometry import normalize


class PanoPoint(object):
    def __init__(self, x, y, z):
        self.direction = normalize((x, y, z), )
