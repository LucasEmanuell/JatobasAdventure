import pygame

class InputHandler:
    def __init__(self):
        self.keys = {} # Estado atual (segurando)
        self.keys_down = set() # Teclas apertadas NESTE frame (bom para menus)
        self.mouse_pos = (0, 0)
        self.mouse_clicked = False

    def update(self):
        # Limpa o estado de "tecla apertada agora" e clique do mouse
        self.keys_down.clear()
        self.mouse_clicked = False
        
        # Atualiza estado contínuo (para andar/correr)
        self.keys = pygame.key.get_pressed()
        
        # Processa fila de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Detecta tecla apertada (Down)
            if event.type == pygame.KEYDOWN:
                self.keys_down.add(event.key)
            
            # Detecta clique do mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pos = pygame.mouse.get_pos()
                self.mouse_clicked = True
            
            # Atualiza posição do mouse mesmo sem clique
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = pygame.mouse.get_pos()
        
        return True

    def is_key_pressed(self, key):
        """Retorna True enquanto a tecla estiver sendo SEGURADA (para andar)"""
        return self.keys[key] if key < len(self.keys) else False

    def was_key_just_pressed(self, key):
        """Retorna True apenas no frame que a tecla foi apertada (para menus)"""
        return key in self.keys_down

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
        # Exemplo simples de toggle
        if self.was_key_just_pressed(pygame.K_h):
            return 1 # Bitmask exemplo
        return 0