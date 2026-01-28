from .base import Entity
from core.vertice import Vertice
import random

class Enemy(Entity):
    def __init__(self, x, y, enemy_type="robot"):
        # Hitbox varia por tipo
        w, h = (70, 100) if enemy_type == "boss" else (50, 80)
        super().__init__(x, y, width=w, height=h)
        
        self.enemy_type = enemy_type
        self.target = None 
        self.attack_cooldown = 0
        
        # Configuração por Tipo
        if self.enemy_type == "robot":
            self.speed = 110.0
            self.health = 60
            self.attack_range = 60
            self.damage = 20
        elif self.enemy_type == "punk": # Inimigo do Trem (Rápido e Fraco)
            self.speed = 160.0
            self.health = 40
            self.attack_range = 50
            self.damage = 15
        elif self.enemy_type == "boss": # Chefão da Rua
            self.speed = 85.0
            self.health = 200
            self.attack_range = 90
            self.damage = 40

    def update(self, dt, player):
        if self.is_dead: return

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        self.target = player
        dx = player.pos[0] - self.pos[0]
        dy = player.pos[1] - self.pos[1]
        dist = (dx**2 + dy**2)**0.5
        target_y_dist = abs(dy)
        
        # IA de Perseguição
        min_dist = 50 if self.enemy_type == "boss" else 40
        
        if dist > min_dist:
            dir_x = dx / dist
            dir_y = dy / dist
            self.pos[0] += dir_x * self.speed * dt
            self.pos[1] += dir_y * self.speed * dt
            if dir_x > 0: self.facing_right = True
            else: self.facing_right = False
            
        # IA de Ataque
        if dist < self.attack_range and target_y_dist < 20 and self.attack_cooldown <= 0:
            self.attack_player(player)

        self.rebuild_model()

    def attack_player(self, player):
        player.take_damage(self.damage)
        self.attack_cooldown = 1.5 
        # Pequeno pulo ao atacar
        self.pos[1] -= 5 

    def rebuild_model(self):
        self.parts = []
        d = 1 if self.facing_right else -1
        
        # Cores baseadas no tipo
        if self.enemy_type == "robot":
            color_body = (200, 50, 50)
            color_eye = (255, 255, 0)
        elif self.enemy_type == "punk":
            color_body = (50, 150, 50) # Verde
            color_eye = (255, 0, 255)  # Rosa choque
        elif self.enemy_type == "boss":
            color_body = (100, 0, 100) # Roxo escuro
            color_eye = (255, 0, 0)    # Olho vermelho
            
        # Pisca se estiver em cooldown de ataque
        if self.attack_cooldown > 1.3: color_body = (255, 255, 255)
        
        # Escala visual
        scale = 1.3 if self.enemy_type == "boss" else 1.0
        
        # CORPO
        self.add_part([
            Vertice((-20*d)*scale, -80*scale), Vertice((20*d)*scale, -80*scale),
            Vertice((15*d)*scale, 0), Vertice((-15*d)*scale, 0)
        ], color_body)
        
        # OLHO/ROSTO
        self.add_part([
            Vertice((5*d)*scale, -70*scale), Vertice((15*d)*scale, -70*scale),
            Vertice((15*d)*scale, -60*scale), Vertice((5*d)*scale, -60*scale)
        ], color_eye)

        # MOICANO (Só pro Punk)
        if self.enemy_type == "punk":
            self.add_part([
                Vertice((-5*d), -80), Vertice((-10*d), -100),
                Vertice((0), -95), Vertice((10*d), -100), Vertice((5*d), -80)
            ], (255, 0, 255))