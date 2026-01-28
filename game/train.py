import math
from core import Vertice
from .entities import Entity

class Train(Entity):
    """Trem de metrô moderno que passa pela janela da estação"""
    def __init__(self, x, y, direction=1):
        super().__init__(x, y)
        self.parallax = 0.08  # Parallax menor para parecer mais distante
        self.direction = direction  # 1 = direita, -1 = esquerda
        self.speed = 200  # Velocidade do metrô
        self.animation_timer = 0
        self.rebuild_train()
    
    def update(self, dt):
        """Atualiza a posição do trem"""
        self.pos[0] += self.speed * self.direction * dt
        self.animation_timer += dt
        self.rebuild_train()
    
    def rebuild_train(self):
        """Reconstroi o modelo do metrô - OTIMIZADO"""
        self.parts = []
        d = self.direction
        
        # Escala maior para o trem
        scale = 2.5
        
        # Cores modernas de metrô
        color_body = (220, 220, 230)      # Cinza claro metálico
        color_stripe = (200, 50, 50)      # Faixa vermelha
        color_window = (100, 150, 200)    # Janelas azuladas
        color_door = (180, 180, 190)      # Portas
        color_dark = (100, 100, 110)      # Detalhes escuros
        
        # === CORPO PRINCIPAL DO METRÔ (1 vagão longo) ===
        
        # Corpo do vagão (retângulo grande)
        body_left = -300 * d * scale
        body_right = 300 * d * scale
        body_top = -80 * scale
        body_bottom = -20 * scale
        
        self.add_part([
            Vertice(body_left, body_top),
            Vertice(body_right, body_top),
            Vertice(body_right, body_bottom),
            Vertice(body_left, body_bottom)
        ], color_body)
        
        # Teto arredondado (topo do vagão)
        roof_height = -90 * scale
        self.add_part([
            Vertice(body_left + 10*d*scale, body_top),
            Vertice(body_right - 10*d*scale, body_top),
            Vertice(body_right - 20*d*scale, roof_height),
            Vertice(body_left + 20*d*scale, roof_height)
        ], (200, 200, 210))
        
        # Faixa vermelha característica (horizontal)
        stripe_y = body_top + 20*scale
        self.add_part([
            Vertice(body_left, stripe_y),
            Vertice(body_right, stripe_y),
            Vertice(body_right, stripe_y + 8*scale),
            Vertice(body_left, stripe_y + 8*scale)
        ], color_stripe)
        
        # === JANELAS (simplificadas para performance) ===
        window_positions = [-240, -160, -80, 0, 80, 160, 240]
        window_width = 60 * scale
        window_height = 35 * scale
        window_y_top = body_top + 35*scale
        
        for wx in window_positions:
            wx_scaled = wx * d * scale
            self.add_part([
                Vertice(wx_scaled, window_y_top),
                Vertice(wx_scaled + window_width*d, window_y_top),
                Vertice(wx_scaled + window_width*d, window_y_top + window_height),
                Vertice(wx_scaled, window_y_top + window_height)
            ], color_window)
        
        # === PORTAS (2 portas) ===
        door_positions = [-100, 100]
        for door_x in door_positions:
            door_x_scaled = door_x * d * scale
            door_width = 50 * scale
            door_height = 50 * scale
            door_y = body_top + 30*scale
            
            # Porta
            self.add_part([
                Vertice(door_x_scaled, door_y),
                Vertice(door_x_scaled + door_width*d, door_y),
                Vertice(door_x_scaled + door_width*d, door_y + door_height),
                Vertice(door_x_scaled, door_y + door_height)
            ], color_door)
            
            # Linha divisória da porta
            mid_x = door_x_scaled + (door_width/2)*d
            self.add_part([
                Vertice(mid_x, door_y),
                Vertice(mid_x + 2*d, door_y),
                Vertice(mid_x + 2*d, door_y + door_height),
                Vertice(mid_x, door_y + door_height)
            ], color_dark)
        
        # === PARTE FRONTAL (nariz do metrô) ===
        if d > 0:  # Indo para direita, nariz na direita
            nose_x = body_right
        else:  # Indo para esquerda, nariz na esquerda
            nose_x = body_left
        
        nose_length = 40 * scale
        
        # Nariz arredondado
        self.add_part([
            Vertice(nose_x, body_top + 10*scale),
            Vertice(nose_x + nose_length*d, body_top + 20*scale),
            Vertice(nose_x + nose_length*d, body_bottom - 5*scale),
            Vertice(nose_x, body_bottom)
        ], (240, 240, 250))
        
        # Farol frontal
        farol_y = body_top + 30*scale
        self.add_part([
            Vertice(nose_x + (nose_length-10)*d, farol_y),
            Vertice(nose_x + nose_length*d, farol_y),
            Vertice(nose_x + nose_length*d, farol_y + 10*scale),
            Vertice(nose_x + (nose_length-10)*d, farol_y + 10*scale)
        ], (255, 255, 100))
        
        # === RODAS/TRILHOS (simplificado) ===
        wheel_y = body_bottom + 5*scale
        wheel_positions = [-200, -100, 0, 100, 200]
        
        for wheel_x in wheel_positions:
            wheel_x_scaled = wheel_x * d * scale
            wheel_size = 8 * scale
            # Rodas simples (retângulos para performance)
            self.add_part([
                Vertice(wheel_x_scaled - wheel_size, wheel_y),
                Vertice(wheel_x_scaled + wheel_size, wheel_y),
                Vertice(wheel_x_scaled + wheel_size, wheel_y + wheel_size),
                Vertice(wheel_x_scaled - wheel_size, wheel_y + wheel_size)
            ], (40, 40, 40))
        
        # Base/chassi
        self.add_part([
            Vertice(body_left + 20*d*scale, body_bottom),
            Vertice(body_right - 20*d*scale, body_bottom),
            Vertice(body_right - 30*d*scale, body_bottom + 10*scale),
            Vertice(body_left + 30*d*scale, body_bottom + 10*scale)
        ], (60, 60, 70))
    
    def get_smoke_particles(self):
        """Não usa partículas de fumaça (metrô elétrico)"""
        return []
