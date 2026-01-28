import pygame
import sys

from core.renderer import Renderer
from core.vertice import Vertice
from engine.camera import Camera
from engine.input import InputHandler
from engine.assets_loader import AssetsLoader
from game.entities import Player, Enemy
from game.levels import GameLevel, Sign
from game.title import TitleScreen 
from game.difficulty import DifficultyScreen
from core.rasterizer import Rasterizer

# --- CONFIGURAÇÕES GERAIS ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LEVEL_WIDTH = 4000 # Definimos um valor padrão para evitar o erro inicial

def draw_sign_labels(renderer, camera, level, font):
    for deco in level.decorations:
        if isinstance(deco, Sign):
            screen_pos = camera.world_to_device(Vertice(deco.pos[0], deco.pos[1]))
            text_surf = font.render(deco.text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(screen_pos.x, screen_pos.y - 105))
            renderer.screen.blit(text_surf, text_rect)

def draw_hearts(renderer, player):
    start_x = 30
    start_y = 30
    size = 15 
    spacing = 40
    
    if player.max_health <= 0: player.max_health = 100
        
    total_hearts = int(player.max_health / 20)
    current_hearts = int(player.health / 20)
    
    if player.health > 0 and player.health % 20 != 0:
        current_hearts += 1

    for i in range(total_hearts):
        color = (255, 0, 0) if i < current_hearts else (50, 50, 50)
        cx = start_x + (i * spacing)
        cy = start_y
        
        heart_shape = [
            Vertice(cx, cy + size), Vertice(cx - size, cy - size/2), 
            Vertice(cx - size/2, cy - size), Vertice(cx, cy - size/2),        
            Vertice(cx + size/2, cy - size), Vertice(cx + size, cy - size/2)  
        ]
        Rasterizer.scanline_fill(renderer.screen, heart_shape, color)

def start_level(level_number, difficulty_hearts, sky_texture, old_player=None):
    # Passamos a textura do céu para o level
    level = GameLevel(level_number, SCREEN_HEIGHT, sky_texture=sky_texture)
    
    if old_player:
        player = old_player
        player.pos = [100, 500] 
        player.health = min(player.health + 20, player.max_health)
    else:
        hp_total = difficulty_hearts * 20
        player = Player(100, 500, max_hp=hp_total)
        
    enemies = level.spawn_entities()
    return player, enemies, level

def main():
    pygame.init()
    pygame.font.init() 

    # --- FONTES ---
    try:
        font_gameover = pygame.font.SysFont('impact', 60)
        font_info = pygame.font.SysFont('arial', 30, bold=True)
        font_sign = pygame.font.SysFont('arial', 20, bold=True)
    except:
        font_gameover = pygame.font.Font(None, 70)
        font_info = pygame.font.Font(None, 40)
        font_sign = pygame.font.Font(None, 25)

    renderer = Renderer(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    camera = Camera(LEVEL_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
    
    input_sys = InputHandler()
    clock = pygame.time.Clock()
    
    # --- CARREGA RECURSOS 
    assets_loader = AssetsLoader()
    # Tenta carregar a textura do céu 
    # Se não existir, o AssetsLoader retorna None e o level usa cor sólida (fallback)
    sky_texture = assets_loader.load_texture("assets/textures/sky.png")
    
    title_screen = TitleScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
    difficulty_screen = DifficultyScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    GAME_STATE = "MENU"
    
    current_level_num = 1
    current_difficulty_hearts = 5 
    
    player = None
    enemies = []
    level = None

    running = True

    while running:
        dt = clock.tick(60) / 1000.0 
        if dt > 0.05: dt = 0.05

        running = input_sys.update()
        
        # --- MENU ---
        if GAME_STATE == "MENU":
            if input_sys.was_key_just_pressed(pygame.K_RETURN):
                GAME_STATE = "DIFFICULTY"
                renderer.screen.fill((0,0,0)) 
            title_screen.draw(renderer)
            title_screen.draw_dynamic(renderer)
            pygame.display.flip()

        # --- DIFICULDADE ---
        elif GAME_STATE == "DIFFICULTY":
            renderer.screen.fill((0,0,0))
            confirm_selection = False
            
            if input_sys.was_key_just_pressed(pygame.K_UP) or input_sys.was_key_just_pressed(pygame.K_w):
                difficulty_screen.move_up()
            if input_sys.was_key_just_pressed(pygame.K_DOWN) or input_sys.was_key_just_pressed(pygame.K_s):
                difficulty_screen.move_down()
            if input_sys.was_key_just_pressed(pygame.K_RETURN) or input_sys.was_key_just_pressed(pygame.K_SPACE):
                confirm_selection = True
            if difficulty_screen.update_mouse(input_sys):
                confirm_selection = True
            
            if confirm_selection:
                current_difficulty_hearts = difficulty_screen.get_selected_hearts()
                current_level_num = 1 
                
                # Inicia o jogo passando a textura do céu
                player, enemies, level = start_level(current_level_num, current_difficulty_hearts, sky_texture)
                camera = Camera(level.width, SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
                
                GAME_STATE = "GAME"
                renderer.screen.fill((0,0,0))
            
            difficulty_screen.draw(renderer)
            renderer.render_step()

        # --- JOGO ---
        elif GAME_STATE == "GAME":
            if not player.is_dead:
                player.update(dt, input_sys, enemies)
                camera.follow(player)
                
                # Fim da fase?
                if player.pos[0] > level.width + 100:
                    current_level_num += 1
                    if current_level_num > 3:
                        GAME_STATE = "VICTORY"
                    else:
                        player, enemies, level = start_level(current_level_num, current_difficulty_hearts, sky_texture, player)
                        camera = Camera(level.width, SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)

                enemies = [e for e in enemies if not e.is_dead]
                for enemy in enemies:
                    enemy.update(dt, player)
            else:
                if input_sys.was_key_just_pressed(pygame.K_r):
                    player, enemies, level = start_level(current_level_num, current_difficulty_hearts, sky_texture)
                    camera = Camera(level.width, SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
                if input_sys.was_key_just_pressed(pygame.K_ESCAPE):
                    GAME_STATE = "MENU"
                    title_screen.reset()
                    renderer.screen.fill((0,0,0))

            if input_sys.is_key_pressed(pygame.K_z): camera.set_zoom(1.5)
            elif input_sys.is_key_pressed(pygame.K_x): camera.set_zoom(1.0)

            renderer.screen.fill((0, 0, 0))

            for bg in level.bg_tiles: renderer.render_background(bg, camera)
            for deco in level.decorations: renderer.render_entity(deco, camera)
            for fl in level.floor_tiles: renderer.render_entity(fl, camera)

            all_entities = enemies + [player]
            all_entities.sort(key=lambda e: e.pos[1])
            for ent in all_entities: renderer.render_entity(ent, camera)
            
            if not player.is_dead:
                draw_hearts(renderer, player)
                draw_sign_labels(renderer, camera, level, font_sign)
            
            if player.is_dead:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                renderer.screen.blit(overlay, (0,0))
                
                go_surf = font_gameover.render("GAME OVER", True, (255, 50, 50))
                go_rect = go_surf.get_rect(center=(SCREEN_WIDTH//2, 250))
                renderer.screen.blit(go_surf, go_rect)

                restart_surf = font_info.render("PRESSIONE R PARA TENTAR NOVAMENTE", True, (200, 200, 200))
                restart_rect = restart_surf.get_rect(center=(SCREEN_WIDTH//2, 350))
                renderer.screen.blit(restart_surf, restart_rect)

            renderer.render_step()

        # --- VITÓRIA ---
        elif GAME_STATE == "VICTORY":
            renderer.screen.fill((20, 20, 50))
            
            vic_surf = font_gameover.render("VOCÊ CHEGOU EM CASA!", True, (100, 255, 100))
            vic_rect = vic_surf.get_rect(center=(SCREEN_WIDTH//2, 200))
            renderer.screen.blit(vic_surf, vic_rect)

            info_surf = font_info.render("JATOBÁ ESTÁ A SALVO", True, (255, 255, 255))
            info_rect = info_surf.get_rect(center=(SCREEN_WIDTH//2, 300))
            renderer.screen.blit(info_surf, info_rect)
            
            esc_surf = font_sign.render("PRESSIONE ESC PARA MENU", True, (150, 150, 200))
            esc_rect = esc_surf.get_rect(center=(SCREEN_WIDTH//2, 450))
            renderer.screen.blit(esc_surf, esc_rect)
            
            if input_sys.was_key_just_pressed(pygame.K_ESCAPE):
                GAME_STATE = "MENU"
                title_screen.reset()
                renderer.screen.fill((0,0,0))
            
            renderer.render_step()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()