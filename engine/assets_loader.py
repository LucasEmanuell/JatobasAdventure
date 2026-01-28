import pygame
import os

class AssetsLoader:
    def __init__(self):
        # Cache para não carregar a mesma imagem várias vezes
        self.textures = {}

    def load_texture(self, path):
        # Verifica se já carregamos esta textura antes
        if path in self.textures:
            return self.textures[path]

        try:
            # Tenta carregar a imagem
            if os.path.exists(path):
                texture = pygame.image.load(path).convert_alpha()
                self.textures[path] = texture
                return texture
            else:
                raise FileNotFoundError
        except Exception:
            print(f"⚠️ Erro: '{path}' não encontrado. Criando textura de fallback.")
            # Cria um quadrado roxo 32x32 para o jogo não travar
            fallback = pygame.Surface((32, 32))
            fallback.fill((255, 0, 255)) 
            return fallback

    @staticmethod
    def get_pixel_from_texture(texture_matrix, u, v):
        tex_w, tex_h = texture_matrix.shape[0], texture_matrix.shape[1]
        
        tx = int(u * (tex_w - 1))
        ty = int(v * (tex_h - 1))
        
        return texture_matrix[tx, ty]