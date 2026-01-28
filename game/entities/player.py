import math
import pygame
from core.vertice import Vertice
from .base import Entity

def move_towards(current, target, max_delta):
    if abs(target - current) <= max_delta:
        return target
    return current + max_delta if target > current else current - max_delta

class Player(Entity):
    # CORREÇÃO AQUI: Adicionado max_hp=100
    def __init__(self, x, y, max_hp=100):
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
        
        # Combate
        self.max_health = max_hp # Usa o valor passado pelo menu
        self.health = max_hp     # Inicia com vida cheia
        self.invincible_timer = 0
        self.is_dead = False
        
        self.attacking = False
        self.attack_timer = 0
        self.attack_duration = 0.3
        self.sword_angle = 0
        
        self.c_skin = (230, 190, 150)
        self.c_armor = (30, 90, 160)
        self.c_sword = (200, 200, 200)

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
            
            if self.pos[1] < self.MIN_Y: self.pos[1] = self.MIN_Y
            if self.pos[1] > self.MAX_Y: self.pos[1] = self.MAX_Y
            
            if self.pos[0] < 20: self.pos[0] = 20
            # Limite maximo horizontal removido aqui, controlado pelo main
            
            if input_x > 0: self.facing_right = True
            elif input_x < 0: self.facing_right = False

        if (input_handler.is_key_pressed(pygame.K_SPACE) or \
            input_handler.is_key_pressed(pygame.K_z)) and not self.attacking:
            self.start_attack()

        if self.attacking:
            self.attack_timer += dt
            progress = min(1.0, self.attack_timer / self.attack_duration)
            self.sword_angle = math.sin(progress * math.pi) * 90 
            
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

    def rebuild_model(self):
        self.parts = []
        d = 1 if self.facing_right else -1
        
        if self.is_dead:
            self.c_skin = (100, 100, 100)
            self.c_armor = (80, 80, 80)
        
        if self.invincible_timer > 0 and int(self.invincible_timer * 20) % 2 == 0:
            return 

        self.add_part([Vertice(-10*d, -95), Vertice(10*d, -95), Vertice(10*d, -75), Vertice(-10*d, -75)], self.c_skin)
        self.add_part([Vertice(-15*d, -75), Vertice(15*d, -75), Vertice(15*d, -35), Vertice(-15*d, -35)], self.c_armor)
        self.add_part([Vertice(-15*d, -35), Vertice(-5*d, -35), Vertice(-5*d, 0), Vertice(-15*d, 0)], (50,50,50))
        self.add_part([Vertice(5*d, -35), Vertice(15*d, -35), Vertice(15*d, 0), Vertice(5*d, 0)], (50,50,50))

        shoulder_x, shoulder_y = 0, -70
        arm_polys = [
            (0, 0), (20*d, 0), (20*d, 10), (0, 10),
            (15*d, -40), (25*d, -40), (25*d, 10), (15*d, 10) 
        ]
        rad = math.radians(self.sword_angle if self.facing_right else -self.sword_angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        final_arm = []
        for x, y in arm_polys:
            rx = x * cos_a - y * sin_a
            ry = x * sin_a + y * cos_a
            final_arm.append(Vertice(shoulder_x + rx, shoulder_y + ry))
            
        self.add_part(final_arm[:4], self.c_armor)
        self.add_part(final_arm[4:], self.c_sword)
