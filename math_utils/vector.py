import math

class JatobasVector:
    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def to_tuple(self):
        return (self.x, self.y)

    def to_homogeneous(self):
        return [self.x, self.y, 1.0]

    def __add__(self, other):
        return JatobasVector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return JatobasVector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return JatobasVector(self.x * scalar, self.y * scalar)

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            return JatobasVector(0, 0)
        return self * (1.0 / mag)

    def __repr__(self):
        return f"JatobasVector({self.x}, {self.y})"