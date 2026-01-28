import pygame

class InputHandler:
    def __init__(self):
        self.keys = {}
        self.mouse_pos = (0, 0)
        self.mouse_clicked = False
        self.events = [] 

    def update(self):
        self.mouse_clicked = False
        self.keys = pygame.key.get_pressed()
        self.events = pygame.event.get()
        
        # --- CORREÇÃO: Atualiza posição do mouse sempre ---
        self.mouse_pos = pygame.mouse.get_pos()
        # --------------------------------------------------
        
        for event in self.events:
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_clicked = True
        
        return True

    def is_key_pressed(self, key):
        return self.keys[key] if key < len(self.keys) else False
    
    def was_key_just_pressed(self, key):
        for event in self.events:
            if event.type == pygame.KEYDOWN:
                if event.key == key:
                    return True
        return False

    def get_movement_vector(self):
        dx, dy = 0, 0
        if self.is_key_pressed(pygame.K_LEFT) or self.is_key_pressed(pygame.K_a):
            dx = -1
        if self.is_key_pressed(pygame.K_RIGHT) or self.is_key_pressed(pygame.K_d):
            dx = 1
        if self.is_key_pressed(pygame.K_UP) or self.is_key_pressed(pygame.K_w):
            dy = -1
        if self.is_key_pressed(pygame.K_DOWN) or self.is_key_pressed(pygame.K_s):
            dy = 1
        return dx, dy

    def debug_hide_entity(self):
        if self.is_key_pressed(pygame.K_t): return 1
        if self.is_key_pressed(pygame.K_y): return 2
        return 0