import math
from core import Vertice
from core.renderer import TILE_WIDTH
from .entities import Entity, Enemy

class EntityTile(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)

class SunEntity(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.parallax = 0.05 
        radius = 50
        segments = 20
        points = []
        for i in range(segments):
            angle = math.radians(i * (360 / segments))
            px = math.cos(angle) * radius
            py = math.sin(angle) * radius
            points.append(Vertice(px, py))
        self.add_part(points, (255, 255, 0)) 

class Sign(Entity):
    def __init__(self, x, y, text_content=""):
        super().__init__(x, y)
        self.text = text_content
        self.add_part([Vertice(-5, 0), Vertice(5, 0), Vertice(5, -80), Vertice(-5, -80)], (50, 50, 50))
        self.add_part([Vertice(-100, -130), Vertice(100, -130), Vertice(100, -80), Vertice(-100, -80)], (20, 40, 100))
        self.add_part([Vertice(-105, -135), Vertice(105, -135), Vertice(105, -130), Vertice(-105, -130)], (200, 200, 200))

class MetroTrain(Entity):
    """Trem de metrô moderno no Level 2 com animação otimizada"""
    def __init__(self, x, y, speed=150, direction=1, level_width=3000):
        super().__init__(x, y)
        self.parallax = 0.15  # Parallax para dar profundidade
        self.speed = speed  # Velocidade do trem (pixels por segundo)
        self.direction = direction  # 1 = direita, -1 = esquerda
        self.level_width = level_width  # Largura do level para loop
        self.initial_x = x  # Posição inicial para reset
        
        # Escala do trem
        self.scale = 1.8
        
        # Cores modernas de metrô
        color_body = (220, 220, 230)      # Cinza claro metálico
        color_stripe = (200, 50, 50)      # Faixa vermelha
        color_window = (100, 150, 200)    # Janelas azuladas
        color_door = (180, 180, 190)      # Portas
        color_dark = (100, 100, 110)      # Detalhes escuros
        
        # Construir geometria apenas uma vez (OTIMIZAÇÃO)
        self._build_train_geometry(color_body, color_stripe, color_window, color_door, color_dark)
    
    def _build_train_geometry(self, color_body, color_stripe, color_window, color_door, color_dark):
        """Constrói a geometria do trem uma única vez (OTIMIZADO)"""
        scale = self.scale
        d = self.direction
        
        # === CORPO PRINCIPAL DO METRÔ ===
        body_left = -250 * scale * d
        body_right = 250 * scale * d
        body_top = -60 * scale
        body_bottom = -10 * scale
        
        # Corpo do vagão
        self.add_part([
            Vertice(body_left, body_top),
            Vertice(body_right, body_top),
            Vertice(body_right, body_bottom),
            Vertice(body_left, body_bottom)
        ], color_body)
        
        # Teto arredondado
        roof_height = -70 * scale
        self.add_part([
            Vertice(body_left + 10*scale*d, body_top),
            Vertice(body_right - 10*scale*d, body_top),
            Vertice(body_right - 20*scale*d, roof_height),
            Vertice(body_left + 20*scale*d, roof_height)
        ], (200, 200, 210))
        
        # Faixa vermelha característica
        stripe_y = body_top + 15*scale
        self.add_part([
            Vertice(body_left, stripe_y),
            Vertice(body_right, stripe_y),
            Vertice(body_right, stripe_y + 6*scale),
            Vertice(body_left, stripe_y + 6*scale)
        ], color_stripe)
        
        # === JANELAS ===
        window_positions = [-200, -130, -60, 10, 80, 150, 220]
        window_width = 50 * scale
        window_height = 30 * scale
        window_y_top = body_top + 28*scale
        
        for wx in window_positions:
            wx_scaled = wx * scale * d
            self.add_part([
                Vertice(wx_scaled, window_y_top),
                Vertice(wx_scaled + window_width*d, window_y_top),
                Vertice(wx_scaled + window_width*d, window_y_top + window_height),
                Vertice(wx_scaled, window_y_top + window_height)
            ], color_window)
        
        # === PORTAS ===
        door_positions = [-80, 80]
        for door_x in door_positions:
            door_x_scaled = door_x * scale * d
            door_width = 45 * scale
            door_height = 45 * scale
            door_y = body_top + 25*scale
            
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
        if d > 0:  # Indo para direita
            nose_x = body_right
        else:  # Indo para esquerda
            nose_x = body_left
        
        nose_length = 35 * scale
        
        # Nariz arredondado
        self.add_part([
            Vertice(nose_x, body_top + 8*scale),
            Vertice(nose_x + nose_length*d, body_top + 15*scale),
            Vertice(nose_x + nose_length*d, body_bottom - 4*scale),
            Vertice(nose_x, body_bottom)
        ], (240, 240, 250))
        
        # Farol frontal
        farol_y = body_top + 25*scale
        self.add_part([
            Vertice(nose_x + (nose_length-8)*d, farol_y),
            Vertice(nose_x + nose_length*d, farol_y),
            Vertice(nose_x + nose_length*d, farol_y + 8*scale),
            Vertice(nose_x + (nose_length-8)*d, farol_y + 8*scale)
        ], (255, 255, 100))
        
        # === RODAS/TRILHOS ===
        wheel_y = body_bottom + 3*scale
        wheel_positions = [-180, -90, 0, 90, 180]
        
        for wheel_x in wheel_positions:
            wheel_x_scaled = wheel_x * scale * d
            wheel_size = 6 * scale
            # Rodas simples
            self.add_part([
                Vertice(wheel_x_scaled - wheel_size, wheel_y),
                Vertice(wheel_x_scaled + wheel_size, wheel_y),
                Vertice(wheel_x_scaled + wheel_size, wheel_y + wheel_size),
                Vertice(wheel_x_scaled - wheel_size, wheel_y + wheel_size)
            ], (40, 40, 40))
        
        # Base/chassi
        self.add_part([
            Vertice(body_left + 20*scale*d, body_bottom),
            Vertice(body_right - 20*scale*d, body_bottom),
            Vertice(body_right - 30*scale*d, body_bottom + 8*scale),
            Vertice(body_left + 30*scale*d, body_bottom + 8*scale)
        ], (60, 60, 70))
    
    def update(self, dt):
        """Atualiza apenas a posição do trem (OTIMIZADO - sem reconstruir geometria)"""
        # Movimenta o trem
        self.pos[0] += self.speed * self.direction * dt
        
        # Sistema de loop: quando o trem sai da tela, volta do outro lado
        if self.direction > 0:  # Indo para direita
            if self.pos[0] > self.level_width + 600:  # Margem de 600 pixels
                self.pos[0] = -600
        else:  # Indo para esquerda
            if self.pos[0] < -600:
                self.pos[0] = self.level_width + 600

class BackgroundTile(EntityTile):
    def __init__(self, tile_x, VIEW_HEIGHT, level_type=1, texture=None):
        super().__init__(tile_x * TILE_WIDTH, 0)
        self.parallax = 0.3
        
        x0, x1 = 0, TILE_WIDTH
        
        if level_type == 1: # ESTRADA (Com Textura de Céu e Montanhas Gradiente)
            HORIZON_Y = 420  # Ajustado para ser rente ao floorTile
            
            # CÉU: Usa textura se houver, senão cor sólida
            if texture:
                total_fatias = 5
                idx_fatia = tile_x % total_fatias
                u0 = idx_fatia / total_fatias
                u1 = (idx_fatia + 1) / total_fatias
                self.add_part([
                    Vertice(x0, 0, u0, 0.0), Vertice(x1, 0, u1, 0.0), 
                    Vertice(x1, HORIZON_Y, u1, 1.0), Vertice(x0, HORIZON_Y, u0, 1.0)
                ], texture=texture)
            else:
                self.add_part([Vertice(x0,0), Vertice(x1,0), Vertice(x1,HORIZON_Y), Vertice(x0,HORIZON_Y)], color=(20, 20, 40)) 

            # MONTANHAS: Com Gradiente - Ajustadas para ficarem menores e próximas ao horizonte
            self.add_part([
                Vertice(x0, HORIZON_Y-20), Vertice(x0+64, HORIZON_Y-80), 
                Vertice(x0+128, HORIZON_Y-40), Vertice(x0+192, HORIZON_Y-70),
                Vertice(x1, HORIZON_Y-30), Vertice(x1, HORIZON_Y), Vertice(x0, HORIZON_Y)
            ], gradient={'top': (60, 70, 90), 'bottom': (30, 35, 50)})
            
        elif level_type == 2: # TREM 
            self.parallax = 0.1 
            WALL_TOP, FLOOR_START = 0, 420
            self.add_part([Vertice(x0,0), Vertice(x1,0), Vertice(x1,FLOOR_START), Vertice(x0,FLOOR_START)], color=(180, 180, 190))
            margin, win_y1, win_y2 = 20, 100, 280
            self.add_part([Vertice(x0+margin, win_y1), Vertice(x1-margin, win_y1), Vertice(x1-margin, win_y2), Vertice(x0+margin, win_y2)], color=(20, 20, 40))
            self.add_part([Vertice(x0+margin+10, win_y1+10), Vertice(x0+margin+30, win_y1+10), Vertice(x0+margin+10, win_y1+30)], color=(40, 40, 60))
            self.add_part([Vertice(x0+margin, 300), Vertice(x1-margin, 300), Vertice(x1-margin, FLOOR_START-10), Vertice(x0+margin, FLOOR_START-10)], color=(150, 50, 50))
            self.add_part([Vertice(x1-15, 0), Vertice(x1, 0), Vertice(x1, FLOOR_START), Vertice(x1-15, FLOOR_START)], color=(140, 140, 150))
            for hx in [60, 128, 190]:
                self.add_part([Vertice(hx, 0), Vertice(hx+2, 0), Vertice(hx+2, 80), Vertice(hx, 80)], (50, 50, 50))
                self.add_part([Vertice(hx-10, 80), Vertice(hx+12, 80), Vertice(hx+12, 95), Vertice(hx-10, 95)], (200, 200, 0))

        elif level_type == 3: # CIDADE 
            HORIZON_Y = 250
            self.add_part([Vertice(x0,0), Vertice(x1,0), Vertice(x1,HORIZON_Y), Vertice(x0,HORIZON_Y)], color=(135, 206, 235))
            self.add_part([Vertice(x0+10, HORIZON_Y-150), Vertice(x0+90, HORIZON_Y-150), Vertice(x0+90, VIEW_HEIGHT), Vertice(x0+10, VIEW_HEIGHT)], color=(80, 80, 100))
            self.add_part([Vertice(x0+100, HORIZON_Y-50), Vertice(x0+240, HORIZON_Y-50), Vertice(x0+240, VIEW_HEIGHT), Vertice(x0+100, VIEW_HEIGHT)], color=(100, 100, 120))

class FloorTile(EntityTile):
    def __init__(self, tile_x, level_type=1):
        super().__init__(tile_x * TILE_WIDTH, 0)
        FLOOR_TOP, FLOOR_BOTTOM = 420, 600
        x0, x1 = 0, TILE_WIDTH
        if level_type == 1:
            self.add_part([Vertice(0, FLOOR_TOP), Vertice(x1, FLOOR_TOP), Vertice(x1, FLOOR_BOTTOM), Vertice(0, FLOOR_BOTTOM)], color=(30, 30, 35))
            self.add_part([Vertice(20, 500), Vertice(100, 500), Vertice(100, 510), Vertice(20, 510)], color=(200, 200, 200))
        elif level_type == 2:
            self.add_part([Vertice(0, FLOOR_TOP), Vertice(x1, FLOOR_TOP), Vertice(x1, FLOOR_BOTTOM), Vertice(0, FLOOR_BOTTOM)], color=(120, 120, 130))
            self.add_part([Vertice(50, 450), Vertice(70, 450), Vertice(60, 460)], (100, 100, 110))
        elif level_type == 3:
            self.add_part([Vertice(0, FLOOR_TOP), Vertice(x1, FLOOR_TOP), Vertice(x1, FLOOR_BOTTOM), Vertice(0, FLOOR_BOTTOM)], color=(180, 180, 180))
            self.add_part([Vertice(0, 420), Vertice(x1, 420), Vertice(x1, 430), Vertice(0, 430)], color=(120, 120, 120))

class House(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.add_part([Vertice(-100, -150), Vertice(100, -150), Vertice(100, 0), Vertice(-100, 0)], color=(220, 200, 180))
        self.add_part([Vertice(-120, -150), Vertice(0, -250), Vertice(120, -150)], color=(180, 60, 60))
        self.add_part([Vertice(-30, -80), Vertice(30, -80), Vertice(30, 0), Vertice(-30, 0)], color=(100, 60, 30))

class GameLevel:
    def __init__(self, level_number, screen_height, sky_texture=None):
        self.level_number = level_number
        self.height = screen_height
        self.sky_texture = sky_texture
        self.bg_tiles = []
        self.floor_tiles = []
        self.enemies_config = [] 
        self.decorations = [] 
        
        # Configs de Level
        if level_number == 1:
            self.width = 4000
            self.enemy_type = "robot"
        elif level_number == 2:
            self.width = 3000
            self.enemy_type = "punk"
        elif level_number == 3:
            self.width = 2500
            self.enemy_type = "boss"

        self.generate_environment()
        self.setup_enemies()

    def generate_environment(self):
        num_tiles = (self.width // TILE_WIDTH) + 4 
        for tx in range(num_tiles):
            # Passa a textura do céu para o BackgroundTile (usada apenas no level 1)
            self.bg_tiles.append(BackgroundTile(tx, self.height, self.level_number, self.sky_texture))
            self.floor_tiles.append(FloorTile(tx, self.level_number))
            
        sign_x = self.width - 250 
        if self.level_number == 1: 
            self.decorations.append(Sign(sign_x, 500, "ESTAÇÃO DE TREM ->"))
        elif self.level_number == 2: 
            self.decorations.append(Sign(sign_x, 500, "SAÍDA ->"))
            # Adicionar trens de metrô ao longo do level 2 com animação otimizada
            # Posicionando trens rentes ao floorTile (Y=433) com velocidades e direções variadas
            # Trem 1: Indo para direita, velocidade média
            self.decorations.append(MetroTrain(800, 433, speed=120, direction=1, level_width=self.width))
            # Trem 2: Indo para esquerda, velocidade rápida
            self.decorations.append(MetroTrain(1800, 433, speed=180, direction=-1, level_width=self.width))
            # Trem 3: Indo para direita, velocidade lenta
            self.decorations.append(MetroTrain(2600, 433, speed=90, direction=1, level_width=self.width))
        elif self.level_number == 3:
            self.decorations.append(SunEntity(600, 80)) 
            self.decorations.append(House(self.width - 200, 500))

    def setup_enemies(self):
        num_groups = self.width // 600
        for i in range(1, num_groups):
            x = i * 600
            count = 1 if self.level_number == 1 else 2
            for k in range(count):
                offset_x = (k * 50)
                self.enemies_config.append((x + offset_x, 500))
        if self.level_number == 3: self.enemies_config.append((self.width - 500, 500))

    def spawn_entities(self):
        enemies = []
        for pos in self.enemies_config:
            etype = self.enemy_type
            if self.level_number == 3 and pos == self.enemies_config[-1]: etype = "boss"
            enemies.append(Enemy(pos[0], pos[1], etype))
        return enemies
