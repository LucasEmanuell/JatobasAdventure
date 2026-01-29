import math
import pygame
from core.vertice import Vertice
from .base import Entity

def move_towards(current, target, max_delta):
    if abs(target - current) <= max_delta:
        return target
    return current + max_delta if target > current else current - max_delta

class Player(Entity):
    # Alterado para aceitar score_multiplier
    def __init__(self, x, y, max_hp=100, score_multiplier=1.0):
        super().__init__(x, y, width=50, height=100)
        
        # --- FÍSICA ---
        self.velocity = [0.0, 0.0]
        self.MAX_SPEED = 320.0
        self.ACCELERATION = 2500.0
        self.FRICTION = 2500.0
        self.Y_SPEED_RATIO = 0.6
        
        # --- LIMITES DO CHÃO ---
        self.MIN_Y = 430 
        self.MAX_Y = 580 
        
        # --- COMBATE & SCORE ---
        self.max_health = max_hp 
        self.health = max_hp     
        self.score = 0
        self.score_multiplier = score_multiplier # Guarda o fator de dificuldade
        
        self.invincible_timer = 0
        self.is_dead = False
        
        self.attacking = False
        self.attack_timer = 0
        self.attack_duration = 0.3
        self.sword_angle = 0
        
        # Animação
        self.walk_cycle = 0
        
        # Cores melhoradas
        self.c_skin = (255, 220, 180)        # Pele mais clara e vibrante
        self.c_hair = (80, 50, 30)           # Cabelo marrom escuro
        self.c_armor = (40, 100, 180)        # Armadura azul royal
        self.c_armor_detail = (60, 140, 220) # Detalhes da armadura
        self.c_belt = (120, 80, 40)          # Cinto marrom
        self.c_sword = (220, 220, 230)       # Espada prateada
        self.c_sword_handle = (100, 60, 30)  # Cabo da espada
        self.c_boots = (60, 40, 20)          # Botas marrom escuro
        self.c_cape = (180, 30, 30)          # Capa vermelha

    def update(self, dt, input_handler, enemies_list):
        if self.is_dead:
            return

        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        input_x, input_y = input_handler.get_movement_vector()
        
        if not self.attacking:
            if input_x != 0 and input_y != 0:
                input_x *= 0.707
                input_y *= 0.707

            target_speed = self.MAX_SPEED
            if input_handler.is_key_pressed(pygame.K_LSHIFT):
                target_speed *= 1.5

            if input_x != 0:
                self.velocity[0] = move_towards(self.velocity[0], input_x * target_speed, self.ACCELERATION * dt)
            else:
                self.velocity[0] = move_towards(self.velocity[0], 0, self.FRICTION * dt)

            if input_y != 0:
                target_y_vel = input_y * target_speed * self.Y_SPEED_RATIO
                self.velocity[1] = move_towards(self.velocity[1], target_y_vel, self.ACCELERATION * dt)
            else:
                self.velocity[1] = move_towards(self.velocity[1], 0, self.FRICTION * dt)

            self.pos[0] += self.velocity[0] * dt
            self.pos[1] += self.velocity[1] * dt
            
            # Atualiza animação de caminhada
            if abs(self.velocity[0]) > 10 or abs(self.velocity[1]) > 10:
                self.walk_cycle += dt * 8
            
            if self.pos[1] < self.MIN_Y: self.pos[1] = self.MIN_Y
            if self.pos[1] > self.MAX_Y: self.pos[1] = self.MAX_Y
            
            if self.pos[0] < 20: self.pos[0] = 20
            
            if input_x > 0: self.facing_right = True
            elif input_x < 0: self.facing_right = False

        if (input_handler.is_key_pressed(pygame.K_SPACE)) and not self.attacking:
            self.start_attack()

        if self.attacking:
            self.attack_timer += dt
            progress = min(1.0, self.attack_timer / self.attack_duration)
            self.sword_angle = math.sin(progress * math.pi) * 120  # Ângulo maior
            
            half_way = self.attack_duration / 2
            if self.attack_timer >= half_way and (self.attack_timer - dt) < half_way:
                self.check_attack_hit(enemies_list)

            if self.attack_timer >= self.attack_duration:
                self.attacking = False
                self.sword_angle = 0

        self.rebuild_model()

    def start_attack(self):
        self.attacking = True
        self.attack_timer = 0
        self.velocity = [0, 0]

    def take_damage(self, amount):
        if self.invincible_timer <= 0 and not self.is_dead:
            self.health -= amount
            self.invincible_timer = 1.0
            self.velocity[0] = -200 if self.facing_right else 200
            
            # --- PENALIDADE ESCALADA ---
            # No hard perde mais pontos também
            penalty = int(50 * self.score_multiplier)
            self.score -= penalty
            if self.score < 0: self.score = 0
            # ---------------------------
            
            if self.health <= 0:
                self.health = 0
                self.is_dead = True
                print("PLAYER MORREU")

    def check_attack_hit(self, enemies):
        reach = 90
        hit_x = self.pos[0] + (20 if self.facing_right else -reach - 20)
        hit_y = self.pos[1] - 80
        attack_rect = (hit_x, hit_y, reach, 80)
        
        for enemy in enemies:
            if enemy.is_dead: continue
            ex, ey, ew, eh = enemy.get_hitbox()
            
            if (attack_rect[0] < ex + ew and
                attack_rect[0] + attack_rect[2] > ex and
                attack_rect[1] < ey + eh and
                attack_rect[1] + attack_rect[3] > ey):
                
                enemy.take_damage(35)
                enemy.pos[0] += 50 if self.facing_right else -50
                
                # --- RECOMPENSA ESCALADA ---
                if enemy.is_dead:
                    # Base 100 * Multiplicador da dificuldade
                    points = int(100 * self.score_multiplier)
                    self.score += points
                    print(f"Kill! +{points} pts")

    def rebuild_model(self):
        self.parts = []
        d = 1 if self.facing_right else -1
        
        # Ajuste de cores quando morto
        if self.is_dead:
            self.c_skin = (120, 120, 120)
            self.c_armor = (80, 80, 80)
            self.c_cape = (100, 40, 40)
        
        # Efeito de invencibilidade (piscar)
        if self.invincible_timer > 0 and int(self.invincible_timer * 20) % 2 == 0:
            return 
        
        # Movimento de caminhada
        walk_offset = math.sin(self.walk_cycle) * 2 if not self.attacking else 0
        leg_offset = math.sin(self.walk_cycle) * 5 if not self.attacking else 0
        
        # === CAPA (atrás) ===
        cape_sway = math.sin(self.walk_cycle * 0.8) * 3
        self.add_part([
            Vertice(-8*d, -85), 
            Vertice(-18*d + cape_sway, -75), 
            Vertice(-18*d + cape_sway, -20),
            Vertice(-10*d, -30)
        ], self.c_cape)
        
        # === CABEÇA ===
        # Rosto
        self.add_part([
            Vertice(-12*d, -95 + walk_offset), 
            Vertice(12*d, -95 + walk_offset), 
            Vertice(12*d, -75 + walk_offset), 
            Vertice(-12*d, -75 + walk_offset)
        ], self.c_skin)
        
        # Cabelo
        self.add_part([
            Vertice(-14*d, -95 + walk_offset), 
            Vertice(14*d, -95 + walk_offset), 
            Vertice(10*d, -88 + walk_offset), 
            Vertice(-10*d, -88 + walk_offset)
        ], self.c_hair)
        
        # Olhos
        eye_x = 5 if self.facing_right else -5
        self.add_part([
            Vertice((eye_x)*d, -88 + walk_offset), 
            Vertice((eye_x+3)*d, -88 + walk_offset), 
            Vertice((eye_x+3)*d, -85 + walk_offset), 
            Vertice((eye_x)*d, -85 + walk_offset)
        ], (50, 50, 50))
        
        # === TORSO ===
        # Corpo principal (armadura)
        self.add_part([
            Vertice(-16*d, -75 + walk_offset), 
            Vertice(16*d, -75 + walk_offset), 
            Vertice(16*d, -35 + walk_offset), 
            Vertice(-16*d, -35 + walk_offset)
        ], self.c_armor)
        
        # Detalhes da armadura (linhas decorativas)
        self.add_part([
            Vertice(-12*d, -70 + walk_offset), 
            Vertice(12*d, -70 + walk_offset), 
            Vertice(12*d, -67 + walk_offset), 
            Vertice(-12*d, -67 + walk_offset)
        ], self.c_armor_detail)
        
        self.add_part([
            Vertice(-10*d, -55 + walk_offset), 
            Vertice(10*d, -55 + walk_offset), 
            Vertice(10*d, -52 + walk_offset), 
            Vertice(-10*d, -52 + walk_offset)
        ], self.c_armor_detail)
        
        # Cinto
        self.add_part([
            Vertice(-16*d, -35 + walk_offset), 
            Vertice(16*d, -35 + walk_offset), 
            Vertice(16*d, -30 + walk_offset), 
            Vertice(-16*d, -30 + walk_offset)
        ], self.c_belt)
        
        # Fivela do cinto
        self.add_part([
            Vertice(-4*d, -34 + walk_offset), 
            Vertice(4*d, -34 + walk_offset), 
            Vertice(4*d, -31 + walk_offset), 
            Vertice(-4*d, -31 + walk_offset)
        ], (200, 180, 100))
        
        # === PERNAS ===
        # Perna esquerda
        self.add_part([
            Vertice(-16*d, -30 + walk_offset), 
            Vertice(-6*d, -30 + walk_offset), 
            Vertice(-6*d, 0 + leg_offset), 
            Vertice(-16*d, 0 - leg_offset)
        ], (60, 60, 80))
        
        # Perna direita
        self.add_part([
            Vertice(6*d, -30 + walk_offset), 
            Vertice(16*d, -30 + walk_offset), 
            Vertice(16*d, 0 - leg_offset), 
            Vertice(6*d, 0 + leg_offset)
        ], (60, 60, 80))
        
        # Botas
        self.add_part([
            Vertice(-16*d, -5 - leg_offset), 
            Vertice(-6*d, -5 + leg_offset), 
            Vertice(-8*d, 0 + leg_offset), 
            Vertice(-18*d, 0 - leg_offset)
        ], self.c_boots)
        
        self.add_part([
            Vertice(6*d, -5 + leg_offset), 
            Vertice(16*d, -5 - leg_offset), 
            Vertice(18*d, 0 - leg_offset), 
            Vertice(8*d, 0 + leg_offset)
        ], self.c_boots)
        
        # === BRAÇO COM ESPADA (animado) ===
        shoulder_x, shoulder_y = 0, -65 + walk_offset
        
        # Polígonos do braço e espada
        arm_base = [(0, 0), (22*d, 0), (22*d, 12), (0, 12)]
        sword_blade = [(20*d, -50), (30*d, -50), (30*d, 15), (20*d, 15)]
        sword_handle = [(20*d, 10), (30*d, 10), (30*d, 18), (20*d, 18)]
        sword_guard = [(18*d, 8), (32*d, 8), (32*d, 12), (18*d, 12)]
        
        # Aplicar rotação da espada
        rad = math.radians(self.sword_angle if self.facing_right else -self.sword_angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        
        # Rotacionar braço
        arm_rotated = []
        for x, y in arm_base:
            rx = x * cos_a - y * sin_a
            ry = x * sin_a + y * cos_a
            arm_rotated.append(Vertice(shoulder_x + rx, shoulder_y + ry))
        
        # Rotacionar lâmina
        blade_rotated = []
        for x, y in sword_blade:
            rx = x * cos_a - y * sin_a
            ry = x * sin_a + y * cos_a
            blade_rotated.append(Vertice(shoulder_x + rx, shoulder_y + ry))
        
        # Rotacionar cabo
        handle_rotated = []
        for x, y in sword_handle:
            rx = x * cos_a - y * sin_a
            ry = x * sin_a + y * cos_a
            handle_rotated.append(Vertice(shoulder_x + rx, shoulder_y + ry))
        
        # Rotacionar guarda
        guard_rotated = []
        for x, y in sword_guard:
            rx = x * cos_a - y * sin_a
            ry = x * sin_a + y * cos_a
            guard_rotated.append(Vertice(shoulder_x + rx, shoulder_y + ry))
        
        # Adicionar partes (ordem importa para sobreposição)
        self.add_part(arm_rotated, self.c_armor)
        self.add_part(blade_rotated, self.c_sword)
        self.add_part(guard_rotated, (180, 160, 100))  # Guarda dourada
        self.add_part(handle_rotated, self.c_sword_handle)
        
        # Efeito de brilho na espada quando atacando
        if self.attacking and self.attack_timer < self.attack_duration * 0.7:
            shine_offset = 10
            shine_poly = []
            for x, y in sword_blade:
                rx = x * cos_a - y * sin_a
                ry = x * sin_a + y * cos_a
                shine_poly.append(Vertice(shoulder_x + rx + shine_offset*d, shoulder_y + ry))
            self.add_part(shine_poly, (255, 255, 255))
