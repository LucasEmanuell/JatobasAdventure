from .base import Entity
from core.vertice import Vertice
import random
import math

class Enemy(Entity):
    def __init__(self, x, y, enemy_type="robot"):
        # Hitbox varia por tipo
        w, h = (70, 100) if enemy_type == "boss" else (50, 80)
        super().__init__(x, y, width=w, height=h)
        
        self.enemy_type = enemy_type
        self.target = None 
        self.attack_cooldown = 0
        self.animation_timer = 0
        
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
            self.damage = 20
        elif self.enemy_type == "boss": # Chefão da Rua
            self.speed = 85.0
            self.health = 200
            self.attack_range = 90
            self.damage = 40

    def update(self, dt, player):
        if self.is_dead: return

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        # Atualiza animação
        self.animation_timer += dt

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
        
        # Animação de caminhada
        walk_bounce = math.sin(self.animation_timer * 8) * 2
        walk_cycle = math.sin(self.animation_timer * 8) * 5
        
        # === ROBOT (VERMELHO - MECANICO) ===
        if self.enemy_type == "robot":
            # Cores
            color_body = (200, 50, 50)
            color_metal = (150, 150, 150)
            color_dark = (100, 30, 30)
            color_eye = (255, 255, 0)
            color_glow = (255, 200, 0)
            
            # Pisca quando vai atacar
            if self.attack_cooldown > 1.3: 
                color_body = (255, 150, 150)
                color_eye = (255, 100, 100)
            
            # Antena/cabeça robótica
            self.add_part([
                Vertice(-3*d, -85 + walk_bounce), 
                Vertice(3*d, -85 + walk_bounce), 
                Vertice(3*d, -95 + walk_bounce), 
                Vertice(-3*d, -95 + walk_bounce)
            ], color_metal)
            
            self.add_part([
                Vertice(-2*d, -95 + walk_bounce), 
                Vertice(2*d, -95 + walk_bounce), 
                Vertice(0, -100 + walk_bounce)
            ], color_glow)
            
            # Cabeça/corpo superior
            self.add_part([
                Vertice(-18*d, -80 + walk_bounce), 
                Vertice(18*d, -80 + walk_bounce),
                Vertice(18*d, -45 + walk_bounce), 
                Vertice(-18*d, -45 + walk_bounce)
            ], color_body)
            
            # Placa de metal no peito
            self.add_part([
                Vertice(-12*d, -70 + walk_bounce), 
                Vertice(12*d, -70 + walk_bounce),
                Vertice(12*d, -55 + walk_bounce), 
                Vertice(-12*d, -55 + walk_bounce)
            ], color_metal)
            
            # Olho (visor)
            self.add_part([
                Vertice((4*d), -75 + walk_bounce), 
                Vertice((14*d), -75 + walk_bounce),
                Vertice((14*d), -68 + walk_bounce), 
                Vertice((4*d), -68 + walk_bounce)
            ], color_eye)
            
            # Detalhes mecânicos (parafusos)
            for offset_y in [-75, -60]:
                self.add_part([
                    Vertice((-10*d), offset_y + walk_bounce), 
                    Vertice((-8*d), offset_y + walk_bounce),
                    Vertice((-8*d), offset_y + 2 + walk_bounce), 
                    Vertice((-10*d), offset_y + 2 + walk_bounce)
                ], color_dark)
            
            # Corpo inferior
            self.add_part([
                Vertice(-16*d, -45 + walk_bounce), 
                Vertice(16*d, -45 + walk_bounce),
                Vertice(14*d, 0), 
                Vertice(-14*d, 0)
            ], color_dark)
            
            # Pernas mecânicas
            self.add_part([
                Vertice(-14*d, -10), 
                Vertice(-6*d, -10),
                Vertice(-6*d, 0 + walk_cycle), 
                Vertice(-16*d, 0 - walk_cycle)
            ], color_metal)
            
            self.add_part([
                Vertice(6*d, -10), 
                Vertice(14*d, -10),
                Vertice(16*d, 0 - walk_cycle), 
                Vertice(6*d, 0 + walk_cycle)
            ], color_metal)
            
            # Braços robóticos
            arm_angle = math.sin(self.animation_timer * 6) * 15
            self.add_part([
                Vertice(-18*d, -70 + walk_bounce), 
                Vertice(-22*d, -70 + walk_bounce + arm_angle),
                Vertice(-22*d, -50 + walk_bounce + arm_angle), 
                Vertice(-18*d, -50 + walk_bounce)
            ], color_metal)
            
            self.add_part([
                Vertice(18*d, -70 + walk_bounce), 
                Vertice(22*d, -70 + walk_bounce - arm_angle),
                Vertice(22*d, -50 + walk_bounce - arm_angle), 
                Vertice(18*d, -50 + walk_bounce)
            ], color_metal)
            
        # === PUNK (VERDE - REBELDE) ===
        elif self.enemy_type == "punk":
            # Cores
            color_body = (50, 150, 50)
            color_skin = (220, 180, 140)
            color_hair = (255, 0, 255)  # Moicano rosa choque
            color_jacket = (40, 40, 40)  # Jaqueta preta
            color_eye = (255, 255, 255)
            
            if self.attack_cooldown > 1.3:
                color_body = (150, 255, 150)
            
            # Moicano punk
            mohawk_points = [
                Vertice((-8*d), -85 + walk_bounce), 
                Vertice((-12*d), -98 + walk_bounce),
                Vertice((-5*d), -95 + walk_bounce),
                Vertice((0), -100 + walk_bounce), 
                Vertice((5*d), -95 + walk_bounce),
                Vertice((12*d), -98 + walk_bounce), 
                Vertice((8*d), -85 + walk_bounce)
            ]
            self.add_part(mohawk_points, color_hair)
            
            # Cabeça
            self.add_part([
                Vertice(-10*d, -85 + walk_bounce), 
                Vertice(10*d, -85 + walk_bounce),
                Vertice(10*d, -70 + walk_bounce), 
                Vertice(-10*d, -70 + walk_bounce)
            ], color_skin)
            
            # Olhos agressivos
            eye_x = 5 if self.facing_right else -5
            self.add_part([
                Vertice((eye_x)*d, -80 + walk_bounce), 
                Vertice((eye_x+3)*d, -80 + walk_bounce),
                Vertice((eye_x+3)*d, -77 + walk_bounce), 
                Vertice((eye_x)*d, -77 + walk_bounce)
            ], color_eye)
            
            # Jaqueta de couro
            self.add_part([
                Vertice(-16*d, -70 + walk_bounce), 
                Vertice(16*d, -70 + walk_bounce),
                Vertice(14*d, -30 + walk_bounce), 
                Vertice(-14*d, -30 + walk_bounce)
            ], color_jacket)
            
            # Detalhes da jaqueta (zíper)
            self.add_part([
                Vertice(0, -70 + walk_bounce), 
                Vertice(2*d, -70 + walk_bounce),
                Vertice(2*d, -30 + walk_bounce), 
                Vertice(0, -30 + walk_bounce)
            ], (200, 200, 200))
            
            # Camiseta verde por baixo
            self.add_part([
                Vertice(-10*d, -70 + walk_bounce), 
                Vertice(10*d, -70 + walk_bounce),
                Vertice(10*d, -55 + walk_bounce), 
                Vertice(-10*d, -55 + walk_bounce)
            ], color_body)
            
            # Calça rasgada
            self.add_part([
                Vertice(-14*d, -30 + walk_bounce), 
                Vertice(14*d, -30 + walk_bounce),
                Vertice(12*d, 0), 
                Vertice(-12*d, 0)
            ], (40, 60, 100))
            
            # Botas pesadas
            self.add_part([
                Vertice(-12*d, -5 - walk_cycle), 
                Vertice(-5*d, -5 + walk_cycle),
                Vertice(-7*d, 0 + walk_cycle), 
                Vertice(-15*d, 0 - walk_cycle)
            ], (50, 50, 50))
            
            self.add_part([
                Vertice(5*d, -5 + walk_cycle), 
                Vertice(12*d, -5 - walk_cycle),
                Vertice(15*d, 0 - walk_cycle), 
                Vertice(7*d, 0 + walk_cycle)
            ], (50, 50, 50))
            
            # Braços com tatuagens
            self.add_part([
                Vertice(-16*d, -65 + walk_bounce), 
                Vertice(-20*d, -60 + walk_bounce),
                Vertice(-20*d, -40 + walk_bounce), 
                Vertice(-16*d, -40 + walk_bounce)
            ], color_skin)
            
            # Tatuagem no braço
            self.add_part([
                Vertice(-18*d, -55 + walk_bounce), 
                Vertice(-17*d, -55 + walk_bounce),
                Vertice(-17*d, -45 + walk_bounce), 
                Vertice(-18*d, -45 + walk_bounce)
            ], (0, 0, 0))
            
        # === BOSS (ROXO - CHEFÃO INTIMIDADOR) ===
        elif self.enemy_type == "boss":
            scale = 1.3
            # Cores
            color_body = (100, 0, 100)
            color_muscle = (120, 20, 120)
            color_dark = (60, 0, 60)
            color_eye = (255, 0, 0)
            color_scar = (200, 0, 0)
            
            if self.attack_cooldown > 1.3:
                color_body = (200, 50, 200)
                color_eye = (255, 200, 200)
            
            # Sombra ameaçadora
            self.add_part([
                Vertice(-15*d*scale, 0), 
                Vertice(15*d*scale, 0),
                Vertice(10*d*scale, 3), 
                Vertice(-10*d*scale, 3)
            ], (0, 0, 0))
            
            # Cabeça grande
            self.add_part([
                Vertice(-20*d*scale, -95*scale + walk_bounce), 
                Vertice(20*d*scale, -95*scale + walk_bounce),
                Vertice(18*d*scale, -70*scale + walk_bounce), 
                Vertice(-18*d*scale, -70*scale + walk_bounce)
            ], color_muscle)
            
            # Cicatriz no rosto
            self.add_part([
                Vertice((2*d)*scale, -88*scale + walk_bounce), 
                Vertice((4*d)*scale, -88*scale + walk_bounce),
                Vertice((6*d)*scale, -75*scale + walk_bounce), 
                Vertice((4*d)*scale, -75*scale + walk_bounce)
            ], color_scar)
            
            # Olhos furiosos
            for eye_off in [8, -8]:
                self.add_part([
                    Vertice((eye_off*d)*scale, -85*scale + walk_bounce), 
                    Vertice((eye_off*d + 5*d)*scale, -85*scale + walk_bounce),
                    Vertice((eye_off*d + 5*d)*scale, -80*scale + walk_bounce), 
                    Vertice((eye_off*d)*scale, -80*scale + walk_bounce)
                ], color_eye)
            
            # Sobrancelhas raivosas
            self.add_part([
                Vertice((5*d)*scale, -86*scale + walk_bounce), 
                Vertice((15*d)*scale, -88*scale + walk_bounce),
                Vertice((15*d)*scale, -86*scale + walk_bounce), 
                Vertice((5*d)*scale, -84*scale + walk_bounce)
            ], color_dark)
            
            # Torso musculoso
            self.add_part([
                Vertice(-25*d*scale, -70*scale + walk_bounce), 
                Vertice(25*d*scale, -70*scale + walk_bounce),
                Vertice(20*d*scale, -20*scale + walk_bounce), 
                Vertice(-20*d*scale, -20*scale + walk_bounce)
            ], color_body)
            
            # Músculos definidos (peitoral)
            self.add_part([
                Vertice(-18*d*scale, -65*scale + walk_bounce), 
                Vertice(-8*d*scale, -65*scale + walk_bounce),
                Vertice(-10*d*scale, -50*scale + walk_bounce), 
                Vertice(-18*d*scale, -50*scale + walk_bounce)
            ], color_muscle)
            
            self.add_part([
                Vertice(8*d*scale, -65*scale + walk_bounce), 
                Vertice(18*d*scale, -65*scale + walk_bounce),
                Vertice(18*d*scale, -50*scale + walk_bounce), 
                Vertice(10*d*scale, -50*scale + walk_bounce)
            ], color_muscle)
            
            # Abdômen
            for i, y in enumerate([-55, -40, -25]):
                width = 16 - i*2
                self.add_part([
                    Vertice((-width*d)*scale, (y*scale) + walk_bounce), 
                    Vertice((width*d)*scale, (y*scale) + walk_bounce),
                    Vertice((width*d)*scale, (y+8)*scale + walk_bounce), 
                    Vertice((-width*d)*scale, (y+8)*scale + walk_bounce)
                ], color_muscle)
            
            # Calça/shorts
            self.add_part([
                Vertice(-20*d*scale, -20*scale + walk_bounce), 
                Vertice(20*d*scale, -20*scale + walk_bounce),
                Vertice(16*d*scale, 0), 
                Vertice(-16*d*scale, 0)
            ], color_dark)
            
            # Braços massivos
            arm_pulse = math.sin(self.animation_timer * 4) * 2
            self.add_part([
                Vertice(-25*d*scale, -65*scale + walk_bounce), 
                Vertice(-32*d*scale, -60*scale + walk_bounce + arm_pulse),
                Vertice(-32*d*scale, -30*scale + walk_bounce + arm_pulse), 
                Vertice(-25*d*scale, -30*scale + walk_bounce)
            ], color_muscle)
            
            self.add_part([
                Vertice(25*d*scale, -65*scale + walk_bounce), 
                Vertice(32*d*scale, -60*scale + walk_bounce - arm_pulse),
                Vertice(32*d*scale, -30*scale + walk_bounce - arm_pulse), 
                Vertice(25*d*scale, -30*scale + walk_bounce)
            ], color_muscle)
            
            # Punhos cerrados
            self.add_part([
                Vertice(-32*d*scale, -30*scale + walk_bounce + arm_pulse), 
                Vertice(-30*d*scale, -30*scale + walk_bounce + arm_pulse),
                Vertice(-30*d*scale, -20*scale + walk_bounce + arm_pulse), 
                Vertice(-32*d*scale, -20*scale + walk_bounce + arm_pulse)
            ], color_dark)
            
            self.add_part([
                Vertice(30*d*scale, -30*scale + walk_bounce - arm_pulse), 
                Vertice(32*d*scale, -30*scale + walk_bounce - arm_pulse),
                Vertice(32*d*scale, -20*scale + walk_bounce - arm_pulse), 
                Vertice(30*d*scale, -20*scale + walk_bounce - arm_pulse)
            ], color_dark)
