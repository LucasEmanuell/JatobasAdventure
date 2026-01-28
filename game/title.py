import pygame
import math
from core.vertice import Vertice
from core.rasterizer import Rasterizer

# --- FONTE VETORIAL ---
VECTOR_FONT = {
    'A': [ [(0, 1), (0.5, 0), (1, 1)],  [(0.25, 0.6), (0.75, 0.6)] ],
    'B': [ [(0, 0), (0.7, 0), (1, 0.2), (1, 0.4), (0.7, 0.5), (0, 0.5), (0,0)],
           [(0, 0.5), (0.7, 0.5), (1, 0.6), (1, 0.9), (0.7, 1), (0, 1), (0, 0.5)] ],
    'C': [ [(1, 0), (0, 0), (0, 1), (1, 1)] ],
    'D': [ [(0, 0), (0.6, 0), (1, 0.4), (1, 0.6), (0.6, 1), (0, 1), (0, 0)] ],
    'E': [ [(1, 0), (0, 0), (0, 1), (1, 1)], [(0, 0.5), (0.6, 0.5)] ],
    'G': [ [(1, 0), (0, 0), (0, 1), (1, 1), (1, 0.5), (0.5, 0.5)] ], 
    'H': [ [(0, 0), (0, 1)], [(1, 0), (1, 1)], [(0, 0.5), (1, 0.5)] ],
    'J': [ [(0.8, 0), (0.8, 0.8), (0.6, 1), (0.2, 1), (0, 0.8)] ],
    'K': [ [(0, 0), (0, 1)], [(1, 0), (0, 0.5), (1, 1)] ],
    'L': [ [(0, 0), (0, 1), (1, 1)] ],
    'N': [ [(0, 1), (0, 0), (1, 1), (1, 0)] ],
    'O': [ [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)] ],
    'P': [ [(0, 1), (0, 0), (1, 0), (1, 0.5), (0, 0.5)] ],
    'R': [ [(0, 1), (0, 0), (1, 0), (1, 0.5), (0, 0.5)], [(0.4, 0.5), (1, 1)] ],
    'S': [ [(1, 0), (0, 0), (0, 0.5), (1, 0.5), (1, 1), (0, 1)] ],
    'T': [ [(0.5, 1), (0.5, 0)], [(0, 0), (1, 0)] ],
    'U': [ [(0, 0), (0, 1), (1, 1), (1, 0)] ],
    'V': [ [(0, 0), (0.5, 1), (1, 0)] ],
    "'": [ [(0.5, 0), (0.5, 0.3)] ],
    ' ': [], 
    'M': [ [(0, 1), (0, 0), (0.5, 0.5), (1, 0), (1, 1)] ] 
}

class TitleScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.blink_timer = 0
        self.is_drawn = False 
        self.building_texture = self.generate_building_texture()

    def generate_building_texture(self):
        w, h = 64, 64
        surface = pygame.Surface((w, h))
        surface.fill((20, 10, 30))
        color_win = (200, 200, 100) 
        color_off = (10, 5, 15)
        import random
        for y in range(4, h, 12):
            for x in range(4, w, 12):
                color = color_win if random.random() > 0.3 else color_off
                pygame.draw.rect(surface, color, (x, y, 6, 8))
        return surface

    def draw_arcade_sky(self, renderer):
        topo1 = (255, 0, 120)
        topo2 = (120, 0, 255)
        base = (10, 0, 30)
        tempo = pygame.time.get_ticks() / 1000
        fator = (math.sin(tempo * 0.5) + 1) / 2
        cor_topo = Rasterizer.interpola_cor(topo1, topo2, fator)
        altura_horizonte = self.height // 2
        for y in range(altura_horizonte):
            t = y / altura_horizonte
            cor = Rasterizer.interpola_cor(cor_topo, base, t)
            renderer.draw_primitive_line(Vertice(0, y), Vertice(self.width, y), cor)

    def draw_arcade_grid(self, renderer):
        horizonte = self.height // 2
        centro_x = self.width // 2
        cor_grid = (255, 0, 255)
        tempo = pygame.time.get_ticks() / 1000
        deslocamento = (tempo * 200) % 40
        
        # Linhas Horizontais (Movimento)
        for i in range(1, 20):
            y = horizonte + i * i * 2 - deslocamento
            if y < self.height:
                renderer.draw_primitive_line(Vertice(0, y), Vertice(self.width, y), cor_grid)
        
        # Linhas Verticais
        for i in range(-12, 13):
            x = centro_x + i * 40
            renderer.draw_primitive_line(Vertice(centro_x, horizonte), Vertice(x, self.height), cor_grid)

    def reset(self):
        self.is_drawn = False
        self.blink_timer = 0

    def draw(self, renderer):
        if not self.is_drawn:
            # Fundo Arcade Novo
            self.draw_arcade_sky(renderer)
            self.draw_arcade_grid(renderer)
            
            # Prédios 
            p1 = [Vertice(50, 600, u=0, v=5), Vertice(50, 250, u=0, v=0), Vertice(150, 250, u=2, v=0), Vertice(150, 600, u=2, v=5)]
            renderer.render_texture_polygon(p1, self.building_texture)
            p2 = [Vertice(160, 600, u=0, v=3), Vertice(160, 400, u=0, v=0), Vertice(290, 400, u=2, v=0), Vertice(290, 600, u=2, v=3)]
            renderer.render_texture_polygon(p2, self.building_texture)
            
            # Lua
            moon_center = Vertice(680, 80)
            renderer.draw_primitive_circle(moon_center, 50, (230, 230, 255))
            renderer.apply_flood_fill(moon_center, (255, 255, 255))
            
            self.is_drawn = True

    def draw_vector_text(self, renderer, text, x, y, size, color, spacing=1.2, thickness=1):
        
        for char in text.upper():
            if char in VECTOR_FONT:
                strokes = VECTOR_FONT[char]
                for stroke in strokes:
                    if len(stroke) > 1:
                        points = []
                        for (nx, ny) in stroke:
                            points.append(Vertice(x + nx * size, y + ny * size))
                        for i in range(len(points) - 1):
                            renderer.draw_primitive_line(points[i], points[i+1], color)
                            if thickness > 1:
                                p1_t = Vertice(points[i].x + 1, points[i].y)
                                p2_t = Vertice(points[i+1].x + 1, points[i+1].y)
                                renderer.draw_primitive_line(p1_t, p2_t, color)
            x += size * spacing

    def draw_dynamic(self, renderer):
        self.draw_vector_text(renderer, "JATOBA'S", 220, 150, 50, (255, 40, 40), 1.1, 2)
        self.draw_vector_text(renderer, "ADVENTURE", 260, 220, 30, (255, 255, 255), 1.1)
        
        # Poça simples
        cx, cy = 400, 520 
        renderer.draw_primitive_ellipse(Vertice(cx, cy), 100, 15, (50, 50, 60))
        
        self.blink_timer += 1
        if self.blink_timer % 60 < 35: 
            self.draw_vector_text(renderer, "PRESS ENTER", 280, 480, 20, (0, 255, 100), 1.1)