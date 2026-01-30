import pygame
import numpy as np

from math_utils.matrix import Matrix3x3
from core.vertice import Vertice
from core.rasterizer import Rasterizer
from core.algorithms import draw_line, draw_ellipse, flood_fill
from core.clipping import cohen_sutherland_clip

TILE_WIDTH = 256

class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self._texture_cache = {} # Cache de texturas

    def put_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.screen.set_at((int(x), int(y)), color)
            
    def draw_primitive_line(self, v1, v2, color):
            clipped = cohen_sutherland_clip(v1, v2, 0, 0, self.width-1, self.height-1)
            if clipped:
                cv1, cv2 = clipped
                draw_line(self, cv1, cv2, color)
            
    def draw_primitive_circle(self, center, radius, color):
        draw_ellipse(self, center, radius, radius, color)

    def draw_primitive_ellipse(self, center, rx, ry, color):
        draw_ellipse(self, center, rx, ry, color)
        
    def apply_flood_fill(self, seed_vertice, color, boundary_color):
        flood_fill(
            self,
            seed=seed_vertice,
            fill_color=color,
            boundary_color=boundary_color,
            use_nearest_neighbors=True
        )
    
    def render_texture_polygon(self, vertices, texture):
        Rasterizer.scanline_texture(self.screen, vertices, texture)
        
    def get_pixel(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return tuple(self.screen.get_at((int(x), int(y))))[:3]
        return (0, 0, 0)

    @staticmethod
    def trasladar(entityposx, entityposy):
        T = Matrix3x3.translation(entityposx, entityposy)
        return Matrix3x3.combine([T])

    def render_entity(self, entity, camera):
        master_matrix = Renderer.trasladar(entity.pos[0], entity.pos[1])
        for part in entity.parts:
            world_vertices = Matrix3x3.apply_transform(part['vertices'], master_matrix)
            screen_vertices = [camera.world_to_device(v) for v in world_vertices]
            
            if part.get('texture') is not None:
                Rasterizer.scanline_texture(self.screen, screen_vertices, part['texture'])
            else:
                Rasterizer.scanline_fill(self.screen, screen_vertices, part['color'])

    def render_background(self, bg_entity, camera):
        cam_x = camera.world_window['x_min']
        offset_x = bg_entity.pos[0] - cam_x * bg_entity.parallax
    
        if offset_x < -800 or offset_x > self.width:
            return

        for part in bg_entity.parts:
            texture = part.get('texture')
            
            if texture:
                # OTIMIZAÇÃO: Blit direto com cache
                vertices = part['vertices']
                # Calcula bounding box
                x_min = min(v.x for v in vertices) + offset_x
                y_min = min(v.y for v in vertices) + bg_entity.pos[1]
                x_max = max(v.x for v in vertices) + offset_x
                y_max = max(v.y for v in vertices) + bg_entity.pos[1]
                
                width = int(x_max - x_min)
                height = int(y_max - y_min)
                
                if width > 0 and height > 0:
                    u_min, u_max = min(v.u for v in vertices), max(v.u for v in vertices)
                    v_min, v_max = min(v.v for v in vertices), max(v.v for v in vertices)
                    
                    cache_key = (id(texture), u_min, u_max, v_min, v_max, width, height)
                    
                    if cache_key not in self._texture_cache:
                        tex_w, tex_h = texture.get_size()
                        src_x = int(u_min * tex_w)
                        src_y = int(v_min * tex_h)
                        src_w = int((u_max - u_min) * tex_w)
                        src_h = int((v_max - v_min) * tex_h)
                        
                        if src_w > 0 and src_h > 0:
                            try:
                                sub_texture = texture.subsurface((src_x, src_y, src_w, src_h))
                                scaled = pygame.transform.scale(sub_texture, (width, height))
                                self._texture_cache[cache_key] = scaled
                            except:
                                self._texture_cache[cache_key] = None
                    
                    cached_texture = self._texture_cache.get(cache_key)
                    if cached_texture:
                        self.screen.blit(cached_texture, (int(x_min), int(y_min)))
                    elif 'color' in part:
                        screen_vertices = [Vertice(v.x + offset_x, v.y + bg_entity.pos[1], v.u, v.v) for v in vertices]
                        Rasterizer.scanline_fill(self.screen, screen_vertices, part['color'])
            
            elif 'gradient' in part:
                # SUPORTE A GRADIENTE (Montanhas)
                screen_vertices = [Vertice(v.x + offset_x, v.y + bg_entity.pos[1], v.u, v.v) for v in part['vertices']]
                Rasterizer.scanline_fill_gradiente(self.screen, screen_vertices, part['gradient']['top'], part['gradient']['bottom'])
            
            elif 'color' in part:
                screen_vertices = [Vertice(v.x + offset_x, v.y + bg_entity.pos[1], v.u, v.v) for v in part['vertices']]
                Rasterizer.scanline_fill(self.screen, screen_vertices, part['color'])

    def render_step(self):
        pygame.display.flip()