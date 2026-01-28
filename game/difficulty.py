import pygame
import math
from core.vertice import Vertice

class DifficultyScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.selected_index = 1 
        self.time = 0
        
        self.options = [
            {"label": "FÁCIL",   "hearts": 7, "color": (100, 255, 100), "desc": "7 Vidas - Modo Passeio"},
            {"label": "MÉDIO",   "mhearts": 5, "color": (255, 255, 100), "desc": "5 Vidas - O Desafio Real"},
            {"label": "DIFÍCIL", "hearts": 3, "color": (255, 50, 50),   "desc": "3 Vidas - Boa Sorte"}
        ]
        
        # Tentativa de carregar fontes melhores
        try:
            self.font_title = pygame.font.SysFont('impact', 70)
            self.font_option = pygame.font.SysFont('arial black', 40)
            self.font_desc = pygame.font.SysFont('calibri', 20, italic=True)
        except:
            self.font_title = pygame.font.Font(None, 80)
            self.font_option = pygame.font.Font(None, 50)
            self.font_desc = pygame.font.Font(None, 30)

        self.button_rects = []
        self.last_mouse_pos = (0, 0)

    def move_up(self):
        self.selected_index = (self.selected_index - 1) % len(self.options)

    def move_down(self):
        self.selected_index = (self.selected_index + 1) % len(self.options)

    def get_selected_hearts(self):
        opt = self.options[self.selected_index]
        return opt.get("hearts", opt.get("mhearts", 5))

    def update_mouse(self, input_sys):
        mx, my = input_sys.mouse_pos
        clicked = input_sys.mouse_clicked
        
        mouse_moved = (mx != self.last_mouse_pos[0] or my != self.last_mouse_pos[1])
        self.last_mouse_pos = (mx, my)

        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint((mx, my)):
                if mouse_moved:
                    self.selected_index = i
                if clicked:
                    self.selected_index = i
                    return True 
        return False

    def draw_grid_background(self, renderer):
        """Grid Cyberpunk no chão"""
        horizon_y = 150
        bottom_y = self.height
        center_x = self.width // 2
        
        # Linhas Verticais (Perspectiva)
        for i in range(-8, 9):
            offset = i * 80
            # Ponto de fuga
            x_top = center_x + (i * 10) 
            x_bottom = center_x + offset * 2
            
            renderer.draw_primitive_line(
                Vertice(x_top, horizon_y), 
                Vertice(x_bottom, bottom_y), 
                (40, 0, 60) # Roxo escuro
            )
            
        # Linhas Horizontais (Progressivas)
        for i in range(15):
            y = horizon_y + (i * i * 2.5) + 10
            if y > self.height: break
            renderer.draw_primitive_line(
                Vertice(0, y), 
                Vertice(self.width, y), 
                (40, 0, 60)
            )

    def draw(self, renderer):
        self.time += 0.1
        self.draw_grid_background(renderer)
        screen = renderer.screen
        cx = self.width // 2
        
        # Título
        title_surf = self.font_title.render("DIFICULDADE", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(cx, 100))
        # Sombra do título
        shadow_surf = self.font_title.render("DIFICULDADE", True, (100, 0, 100))
        screen.blit(shadow_surf, (title_rect.x + 4, title_rect.y + 4))
        screen.blit(title_surf, title_rect)

        self.button_rects = []
        start_y = 250
        spacing = 90
        
        for i, opt in enumerate(self.options):
            is_selected = (i == self.selected_index)
            
            color = opt["color"] if is_selected else (80, 80, 80)
            
            # Efeito de pulsação se selecionado
            scale_factor = 1.0
            if is_selected:
                scale_factor = 1.05 + 0.05 * math.sin(self.time)
            
            # Renderiza texto
            label_surf = self.font_option.render(opt["label"], True, color)
            
            # Aplica escala simples (transformando a surface) se selecionado
            if is_selected:
                w = int(label_surf.get_width() * scale_factor)
                h = int(label_surf.get_height() * scale_factor)
                label_surf = pygame.transform.scale(label_surf, (w, h))
            
            label_rect = label_surf.get_rect(center=(cx, start_y + i * spacing))
            
            # Hitbox mouse
            self.button_rects.append(label_rect.inflate(150, 40))
            
            screen.blit(label_surf, label_rect)
            
            if is_selected:
                # Descrição
                desc_surf = self.font_desc.render(opt["desc"], True, (200, 200, 200))
                desc_rect = desc_surf.get_rect(center=(cx, label_rect.bottom + 20))
                screen.blit(desc_surf, desc_rect)
                
                # Linhas decorativas laterais
                line_y = label_rect.centery
                margin = 20 + int(5 * math.sin(self.time * 2))
                
                renderer.draw_primitive_line(
                    Vertice(label_rect.left - margin - 20, line_y),
                    Vertice(label_rect.left - margin, line_y),
                    color
                )
                renderer.draw_primitive_line(
                    Vertice(label_rect.right + margin, line_y),
                    Vertice(label_rect.right + margin + 20, line_y),
                    color
                )

        # Rodapé
        footer_surf = self.font_desc.render("USE [W/S] OU MOUSE  •  ENTER PARA INICIAR", True, (100, 100, 150))
        footer_rect = footer_surf.get_rect(center=(cx, self.height - 30))
        screen.blit(footer_surf, footer_rect)