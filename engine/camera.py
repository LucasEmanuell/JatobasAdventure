from core import Vertice

class Camera():
    def __init__(self, world_width, world_height, screen_width, screen_height):
        # Define o tamanho total do mundo (Level)
        self.world_window = {
            'x_min': 0, 'y_min': 0,
            'x_max': world_width, 'y_max': world_height # Agora aceita tamanho dinâmico
        }
        
        self.viewport = {
            'x_min': 0, 'y_min': 0,
            'x_max': screen_width, 'y_max': screen_height
        }
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Fator de Zoom atual
        self.zoom_level = 1.0

    def set_zoom(self, level):
        self.zoom_level = level
        # Recalcula a janela baseado no centro atual
        center_x = (self.world_window['x_min'] + self.world_window['x_max']) / 2
        center_y = (self.world_window['y_min'] + self.world_window['y_max']) / 2
        self._update_window_size(center_x, center_y)

    def follow(self, target_entity):
        """
        Faz a câmera seguir uma entidade (Player), mantendo-a no centro X.
        Respeita os limites do mundo (0 até world_width).
        """
        # O centro desejado é a posição do player
        target_x = target_entity.pos[0]
        # O centro Y mantemos fixo no meio da tela (ou pode seguir se quiser pular alto)
        target_y = self.screen_height / 2 

        # Calcula largura da janela visual em coordenadas de mundo
        view_w = (self.screen_width) / self.zoom_level
        view_h = (self.screen_height) / self.zoom_level
        
        # Calcula os novos limites tentativos
        new_x_min = target_x - view_w / 2
        new_x_max = target_x + view_w / 2
        
        # --- CLAMP (Travar nos cantos do mapa) ---
        # Se tentar ir para a esquerda do zero
        if new_x_min < 0:
            new_x_min = 0
            new_x_max = view_w
            
        # Se tentar ir para a direita do fim do mundo (precisamos saber o limite total do level)
        # Assumindo que o limite máximo foi passado no init como world_width original?
        # Para simplificar, vamos travar apenas se tivermos essa info. 
        # No init self.world_window['x_max'] guarda a janela ATUAL, não o mundo todo.
        # Vamos assumir que o mundo acaba onde definimos no main.
        
        self.world_window['x_min'] = new_x_min
        self.world_window['x_max'] = new_x_max
        # Y geralmente não muda em beat em up horizontal
        self.world_window['y_min'] = 0
        self.world_window['y_max'] = self.screen_height

    def _update_window_size(self, cx, cy):
        new_half_width = (self.screen_width / 2) / self.zoom_level
        new_half_height = (self.screen_height / 2) / self.zoom_level
        
        self.world_window['x_min'] = cx - new_half_width
        self.world_window['x_max'] = cx + new_half_width
        self.world_window['y_min'] = cy - new_half_height
        self.world_window['y_max'] = cy + new_half_height

    def world_to_device(self, v: Vertice) -> Vertice:
        # Transformação Janela -> Viewport
        sx = (
            (self.viewport['x_max'] - self.viewport['x_min']) /
            (self.world_window['x_max'] - self.world_window['x_min'])
        )
        sy = (
            (self.viewport['y_max'] - self.viewport['y_min']) /
            (self.world_window['y_max'] - self.world_window['y_min'])
        )

        dx = self.viewport['x_min'] + (v.x - self.world_window['x_min']) * sx
        dy = self.viewport['y_min'] + (v.y - self.world_window['y_min']) * sy

        return Vertice(int(dx), int(dy), v.u, v.v)