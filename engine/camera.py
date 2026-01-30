import numpy as np
from core import Vertice
from math_utils.matrix import Matrix3x3 

class Camera():
    def __init__(self, world_width, world_height, screen_width, screen_height):
        # Janela do Mundo (O que a câmera vê)
        self.world_window = {
            'x_min': 0, 'y_min': 0,
            'x_max': world_width, 'y_max': world_height
        }
        
        # Viewport (A tela física)
        self.viewport = {
            'x_min': 0, 'y_min': 0,
            'x_max': screen_width, 'y_max': screen_height
        }
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.zoom_level = 1.0
        
        # Inicializa a matriz de identidade
        self.transform_matrix = Matrix3x3.identity()
        
        # Calcula a primeira matriz
        self._update_transformation_matrix()

    def _update_transformation_matrix(self):
        """
        Recalcula a matriz World-to-Viewport baseada na teoria da Aula 11 (Slide 18).
        Fórmula: M = T2 * S * T1
        """
        # 1. T1: Translação (Window -> Origem)
        # Move o canto inferior esquerdo da window para (0,0)
        tx1 = -self.world_window['x_min']
        ty1 = -self.world_window['y_min']
        t1 = Matrix3x3.translation(tx1, ty1)

        # 2. S: Escala (Normalização Window -> Viewport)
        # Calcula a proporção entre o tamanho do mundo visto e o tamanho da tela
        ww_width = self.world_window['x_max'] - self.world_window['x_min']
        ww_height = self.world_window['y_max'] - self.world_window['y_min']
        
        vp_width = self.viewport['x_max'] - self.viewport['x_min']
        vp_height = self.viewport['y_max'] - self.viewport['y_min']

        # Proteção contra divisão por zero
        if ww_width == 0: ww_width = 1
        if ww_height == 0: ww_height = 1

        sx = vp_width / ww_width
        sy = vp_height / ww_height
        s = Matrix3x3.scale(sx, sy)

        # 3. T2: Translação (Origem -> Viewport)
        # Move para a posição inicial do viewport (geralmente 0,0)
        tx2 = self.viewport['x_min']
        ty2 = self.viewport['y_min']
        t2 = Matrix3x3.translation(tx2, ty2)

        # COMPOSIÇÃO DE MATRIZES
        # A ordem de aplicação no vetor é: T1 primeiro, depois S, depois T2.
        # Matematicamente: v' = T2 * S * T1 * v
        # Na nossa lib Matrix3x3.combine, passamos na ordem inversa da aplicação lógica
        # ou direta dependendo da implementação do dot product. 
        # Para garantir: M = T2 @ S @ T1
        
        m_temp = np.dot(s, t1)        # S * T1
        self.transform_matrix = np.dot(t2, m_temp) # T2 * (S * T1)

    def set_zoom(self, level):
        self.zoom_level = level
        # Acha o centro atual
        center_x = (self.world_window['x_min'] + self.world_window['x_max']) / 2
        center_y = (self.world_window['y_min'] + self.world_window['y_max']) / 2
        
        # Recalcula tamanho da janela baseado no zoom
        self._update_window_size(center_x, center_y)
        
        # Importante: Atualizar a matriz após mudar a janela
        self._update_transformation_matrix()

    def follow(self, target_entity):
        """
        Faz a câmera seguir o Player (Panning)
        """
        target_x = target_entity.pos[0]
        
        # Largura da visão atual (considerando zoom)
        view_w = (self.screen_width) / self.zoom_level
        
        new_x_min = target_x - view_w / 2
        new_x_max = target_x + view_w / 2
        
        # Clamp (Não deixa a câmera sair do mapa à esquerda)
        if new_x_min < 0:
            new_x_min = 0
            new_x_max = view_w
            
        self.world_window['x_min'] = new_x_min
        self.world_window['x_max'] = new_x_max
        self.world_window['y_min'] = 0
        self.world_window['y_max'] = self.screen_height
        
        # Importante: Atualizar a matriz após mover a câmera
        self._update_transformation_matrix()

    def _update_window_size(self, cx, cy):
        new_half_width = (self.screen_width / 2) / self.zoom_level
        new_half_height = (self.screen_height / 2) / self.zoom_level
        
        self.world_window['x_min'] = cx - new_half_width
        self.world_window['x_max'] = cx + new_half_width
        self.world_window['y_min'] = cy - new_half_height
        self.world_window['y_max'] = cy + new_half_height

    def world_to_device(self, v: Vertice) -> Vertice:
        """
        Aplica a Matriz de Transformação M ao vértice.
        """
        # 1. Converte vértice para coordenadas homogêneas (x, y, 1)
        vec = np.array([v.x, v.y, 1.0])
        
        # 2. Multiplicação Matricial: res = M * v
        res = self.transform_matrix @ vec
        
        # 3. Retorna novo vértice com coordenadas de tela (inteiros)
        return Vertice(int(res[0]), int(res[1]), v.u, v.v)