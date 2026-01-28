import math
from core.vertice import Vertice

class Entity:
    def __init__(self, x, y, width=40, height=100):
        self.pos = [x, y]
        self.vel = [0, 0]
        self.width = width 
        self.height = height
        self.health = 100
        self.max_health = 100
        self.is_dead = False
        self.facing_right = True 
        self.parts = []
        self.color_tint = (255, 255, 255)

    def add_part(self, vertices, color=None, texture=None, gradient=None):
        part = {'vertices': vertices}
        
        if texture is not None:
            part['texture'] = texture
        elif gradient is not None:
            # Suporte a gradiente
            part['gradient'] = gradient
        elif color is not None:
            part['color'] = color
        else:
            part['color'] = (255, 255, 255)
        
        self.parts.append(part)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.is_dead = True

    def get_hitbox(self):
        return (self.pos[0] - self.width // 2, self.pos[1] - self.height, self.width, self.height)

    def check_collision(self, other_entity):
        r1 = self.get_hitbox()
        r2 = other_entity.get_hitbox()
        return (r1[0] < r2[0] + r2[2] and r1[0] + r1[2] > r2[0] and r1[1] < r2[1] + r2[3] and r1[1] + r1[3] > r2[1])

    def update(self, dt):
        pass