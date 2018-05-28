import numpy


def normalize(v):
    norm = numpy.linalg.norm(v)
    return v * 1.0/norm
