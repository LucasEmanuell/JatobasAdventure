import numpy as np
import math

from core.vertice import Vertice

class Matrix3x3:

    @staticmethod
    def identity():
        return np.eye(3)

    @staticmethod
    def translation(dx, dy):
        matrix = np.eye(3)
        matrix[0, 2] = dx
        matrix[1, 2] = dy
        return matrix

    @staticmethod
    def scale(sx, sy):
        matrix = np.eye(3)
        matrix[0, 0] = sx
        matrix[1, 1] = sy
        return matrix

    @staticmethod
    def rotation(degrees):
        angle = math.radians(degrees)
        c = math.cos(angle)
        s = math.sin(angle)
        matrix = np.eye(3)
        matrix[0, 0] = c
        matrix[0, 1] = -s
        matrix[1, 0] = s
        matrix[1, 1] = c
        return matrix

    @staticmethod
    def combine(matrices):
        result = Matrix3x3.identity()
        for m in matrices:
            result = np.dot(m, result)
        return result

    @staticmethod
    def apply_transform(vertices, matrix):
        transformed = []
        for v in vertices:
            vec = np.array([v.x, v.y, 1.0])
            res = matrix @ vec
            transformed.append(
                Vertice(res[0], res[1], v.u, v.v)
            )
        return transformed