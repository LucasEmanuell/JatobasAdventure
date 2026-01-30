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
from game.highscore import HighScoreManager 
from core.rasterizer import Rasterizer

# --- CONFIGURAÇÕES GERAIS ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LEVEL_WIDTH = 4000

# Configurações do Minimapa (Viewport Secundário)
MINIMAP_W = 250
MINIMAP_H = 40
MINIMAP_X = SCREEN_WIDTH - MINIMAP_W - 30
MINIMAP_Y = 70

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

def draw_score(renderer, player, font):
    score_text = f"SCORE: {player.score:06d}"
    shadow = font.render(score_text, True, (0, 0, 0))
    renderer.screen.blit(shadow, (SCREEN_WIDTH - 248, 28))
    text = font.render(score_text, True, (255, 255, 100))
    renderer.screen.blit(text, (SCREEN_WIDTH - 250, 26))
    
def draw_minimap(renderer, player, level, mini_camera):
    """
    Desenha o minimapa usando uma Segunda Câmera (Matriz de Transformação).
    Isso prova a reutilização da lógica de Window-to-Viewport.
    """
    
    # 1. DESENHO DO FUNDO E HUD 
    # Cores
    bg_color = (20, 20, 30, 100)
    border_color = (100, 100, 150, 120)
    track_color = (50, 50, 70, 150)
    flag_color = (255, 50, 50)
    
    # Surface transparente para o minimapa
    minimap_surface = pygame.Surface((MINIMAP_W, MINIMAP_H), pygame.SRCALPHA)
    
    # Fundo e Borda
    pygame.draw.rect(minimap_surface, bg_color, (0, 0, MINIMAP_W, MINIMAP_H))
    pygame.draw.rect(minimap_surface, border_color, (0, 0, MINIMAP_W, MINIMAP_H), 2)
    
    # Linha do trilho (chão)
    track_y = MINIMAP_H // 2 + 10
    pygame.draw.line(minimap_surface, track_color, (5, track_y), (MINIMAP_W - 5, track_y), 3)
    
    # Bandeira no final
    flag_x = MINIMAP_W - 10
    flag_y = track_y
    pygame.draw.line(minimap_surface, (200, 200, 200), (flag_x, flag_y - 12), (flag_x, flag_y + 5), 2)
    flag_points = [(flag_x, flag_y - 12), (flag_x + 12, flag_y - 7), (flag_x, flag_y - 2)]
    pygame.draw.polygon(minimap_surface, flag_color, flag_points)
    
    # Renderiza a base do minimapa na tela principal
    renderer.screen.blit(minimap_surface, (MINIMAP_X, MINIMAP_Y))
    
    # 2. DESENHO DO PLAYER
    # Usamos mini_camera.world_to_device()
    
    for part in player.parts:
        points = []
        for v in part['vertices']:
            # Transforma o vértice local do player para coordenadas do mundo
            # (O player é definido relativo ao centro dele, então somamos a posição)
            world_x = player.pos[0] + v.x
            world_y = player.pos[1] + v.y
            
            # Pede para a Câmera do Minimapa converter Mundo -> Viewport do Minimapa
            v_screen = mini_camera.world_to_device(Vertice(world_x, world_y))
            
            # O resultado v_screen está em coordenadas relativas ao viewport (0..250)
            # Precisamos somar o offset de onde o minimapa está na tela global
            final_x = v_screen.x + MINIMAP_X
            final_y = v_screen.y + MINIMAP_Y 
            
            points.append((final_x, final_y))
        
        # Desenha o polígono transformado
        color = part.get('color', (200, 200, 200))
        if len(points) >= 3:
            # Desenhamos direto na tela do renderer para não perder qualidade alpha
            pygame.draw.polygon(renderer.screen, color, points)

def start_level(level_number, difficulty_hearts, sky_texture, old_player=None):
    level = GameLevel(level_number, SCREEN_HEIGHT, sky_texture=sky_texture)
    
    if old_player:
        player = old_player
        player.pos = [100, 500] 
        player.health = min(player.health + 20, player.max_health)
    else:
        hp_total = difficulty_hearts * 20
        multiplier = 1.0
        if difficulty_hearts == 5: multiplier = 1.5
        elif difficulty_hearts <= 3: multiplier = 3.0
            
        player = Player(100, 500, max_hp=hp_total, score_multiplier=multiplier)
        
    enemies = level.spawn_entities()
    return player, enemies, level

# Atualizado para receber mini_camera
def render_game_scene(renderer, camera, mini_camera, level, player, enemies, font_sign, font_score):
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
        draw_score(renderer, player, font_score)
        # Passamos a mini_camera aqui
        draw_minimap(renderer, player, level, mini_camera)

def main():
    pygame.init()
    pygame.font.init() 

    try:
        font_gameover = pygame.font.SysFont('impact', 60)
        font_info = pygame.font.SysFont('arial', 30, bold=True)
        font_sign = pygame.font.SysFont('arial', 20, bold=True)
        font_score = pygame.font.SysFont('consolas', 28, bold=True) 
    except:
        font_gameover = pygame.font.Font(None, 70)
        font_info = pygame.font.Font(None, 40)
        font_sign = pygame.font.Font(None, 25)
        font_score = pygame.font.Font(None, 35)

    renderer = Renderer(SCREEN_WIDTH, SCREEN_HEIGHT)
    input_sys = InputHandler()
    clock = pygame.time.Clock()
    
    assets_loader = AssetsLoader()
    sky_texture = assets_loader.load_texture("assets/textures/sky.png")
    
    # --- CÂMERA PRINCIPAL ---
    # Janela: Móvel (define no update) | Viewport: Tela Inteira (800x600)
    camera = Camera(LEVEL_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # --- CÂMERA DO MINIMAPA (NOVA!) ---
    # Janela: O Level INTEIRO (0..4000) | Viewport: Tamanho do Minimapa (250x40)
    # Isso cria uma matriz de escala que reduz tudo para caber no minimapa
    mini_camera = Camera(LEVEL_WIDTH, SCREEN_HEIGHT, MINIMAP_W, MINIMAP_H)
    
    title_screen = TitleScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
    difficulty_screen = DifficultyScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
    hs_manager = HighScoreManager("scores.json")
    
    GAME_STATE = "MENU"
    current_level_num = 1
    current_difficulty_hearts = 5 
    
    player = None
    enemies = []
    level = None
    player_name_input = ""
    blink_cursor = 0

    running = True

    while running:
        dt = clock.tick(60) / 1000.0 
        if dt > 0.05: dt = 0.05
        running = input_sys.update()
        
        if GAME_STATE == "MENU":
            if input_sys.was_key_just_pressed(pygame.K_RETURN):
                GAME_STATE = "DIFFICULTY"
                renderer.screen.fill((0,0,0)) 
            renderer.screen.fill((0,0,0)) 
            title_screen.draw(renderer)
            title_screen.draw_dynamic(renderer)
            pygame.display.flip()

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
                player, enemies, level = start_level(current_level_num, current_difficulty_hearts, sky_texture)
                
                # Reseta câmeras para o novo level (importante se a largura do level mudar)
                camera = Camera(level.width, SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
                # O minimapa precisa saber que o "Mundo" mudou de tamanho
                mini_camera = Camera(level.width, SCREEN_HEIGHT, MINIMAP_W, MINIMAP_H)
                
                GAME_STATE = "GAME"
                renderer.screen.fill((0,0,0))
            
            difficulty_screen.draw(renderer)
            renderer.render_step()

        elif GAME_STATE == "GAME":
            if not player.is_dead:
                player.update(dt, input_sys, enemies)
                camera.follow(player)
                
                if player.pos[0] > level.width + 100:
                    current_level_num += 1
                    if current_level_num > 3:
                        GAME_STATE = "VICTORY"
                    else:
                        player, enemies, level = start_level(current_level_num, current_difficulty_hearts, sky_texture, player)
                        camera = Camera(level.width, SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
                        mini_camera = Camera(level.width, SCREEN_HEIGHT, MINIMAP_W, MINIMAP_H)

                enemies = [e for e in enemies if not e.is_dead]
                for enemy in enemies:
                    enemy.update(dt, player)
                
                for deco in level.decorations:
                    deco.update(dt)
                
                if input_sys.was_key_just_pressed(pygame.K_ESCAPE):
                    GAME_STATE = "PAUSE"
            else:
                if input_sys.was_key_just_pressed(pygame.K_r) or input_sys.was_key_just_pressed(pygame.K_RETURN):
                    if player.score > 0:
                        player_name_input = "" 
                        GAME_STATE = "INPUT_NAME" 
                    else:
                        GAME_STATE = "MENU"
                        title_screen.reset()
                    renderer.screen.fill((0,0,0)) 
                
                if input_sys.was_key_just_pressed(pygame.K_ESCAPE):
                    GAME_STATE = "MENU"
                    title_screen.reset()
                    renderer.screen.fill((0,0,0)) 

            if input_sys.is_key_pressed(pygame.K_z): camera.set_zoom(1.5)
            elif input_sys.is_key_pressed(pygame.K_x): camera.set_zoom(1.0)

            # Passa a mini_camera aqui
            render_game_scene(renderer, camera, mini_camera, level, player, enemies, font_sign, font_score)
            
            if player.is_dead:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                renderer.screen.blit(overlay, (0,0))
                
                go_surf = font_gameover.render("GAME OVER", True, (255, 50, 50))
                go_rect = go_surf.get_rect(center=(SCREEN_WIDTH//2, 200))
                renderer.screen.blit(go_surf, go_rect)

                final_score_surf = font_info.render(f"SCORE FINAL: {player.score}", True, (255, 255, 100))
                renderer.screen.blit(final_score_surf, final_score_surf.get_rect(center=(SCREEN_WIDTH//2, 300)))

                msg = "PRESSIONE [ENTER] PARA REGISTRAR" if player.score > 0 else "PRESSIONE [ENTER] PARA SAIR"
                cont_surf = font_info.render(msg, True, (200, 200, 200))
                renderer.screen.blit(cont_surf, cont_surf.get_rect(center=(SCREEN_WIDTH//2, 400)))

            renderer.render_step()

        elif GAME_STATE == "PAUSE":
            render_game_scene(renderer, camera, mini_camera, level, player, enemies, font_sign, font_score)
            
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            renderer.screen.blit(overlay, (0,0))
            
            pause_title = font_gameover.render("JOGO PAUSADO", True, (255, 255, 255))
            renderer.screen.blit(pause_title, pause_title.get_rect(center=(SCREEN_WIDTH//2, 200)))
            
            resume_surf = font_info.render("PRESSIONE [ENTER] PARA CONTINUAR", True, (100, 255, 100))
            renderer.screen.blit(resume_surf, resume_surf.get_rect(center=(SCREEN_WIDTH//2, 300)))
            
            quit_surf = font_info.render("PRESSIONE [Q] PARA SAIR AO MENU", True, (255, 100, 100))
            renderer.screen.blit(quit_surf, quit_surf.get_rect(center=(SCREEN_WIDTH//2, 380)))
            
            if input_sys.was_key_just_pressed(pygame.K_RETURN):
                GAME_STATE = "GAME"
            
            if input_sys.was_key_just_pressed(pygame.K_q):
                GAME_STATE = "MENU"
                title_screen.reset()
                renderer.screen.fill((0,0,0))

            renderer.render_step()

        elif GAME_STATE == "VICTORY":
            renderer.screen.fill((20, 20, 50))
            
            vic_surf = font_gameover.render("VOCÊ CHEGOU EM CASA!", True, (100, 255, 100))
            renderer.screen.blit(vic_surf, vic_surf.get_rect(center=(SCREEN_WIDTH//2, 180)))

            score_surf = font_gameover.render(f"SCORE TOTAL: {player.score}", True, (255, 255, 0))
            renderer.screen.blit(score_surf, score_surf.get_rect(center=(SCREEN_WIDTH//2, 300)))
            
            msg = "PRESSIONE ENTER PARA REGISTRAR" if player.score > 0 else "PRESSIONE ENTER PARA MENU"
            esc_surf = font_sign.render(msg, True, (150, 150, 200))
            renderer.screen.blit(esc_surf, esc_surf.get_rect(center=(SCREEN_WIDTH//2, 450)))
            
            if input_sys.was_key_just_pressed(pygame.K_RETURN) or input_sys.was_key_just_pressed(pygame.K_ESCAPE):
                if player.score > 0 and not input_sys.was_key_just_pressed(pygame.K_ESCAPE):
                    player_name_input = ""
                    GAME_STATE = "INPUT_NAME"
                else:
                    GAME_STATE = "MENU"
                    title_screen.reset()
                renderer.screen.fill((0,0,0)) 
            
            renderer.render_step()

        elif GAME_STATE == "INPUT_NAME":
            renderer.screen.fill((0, 0, 0))
            title = font_gameover.render("DIGITE SEU NOME", True, (0, 255, 255))
            renderer.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 150)))
            score_display = font_info.render(f"SCORE: {player.score}", True, (255, 255, 0))
            renderer.screen.blit(score_display, score_display.get_rect(center=(SCREEN_WIDTH//2, 220)))

            for evt in input_sys.events:
                if evt.type == pygame.KEYDOWN:
                    if evt.key == pygame.K_RETURN:
                        final_name = player_name_input if player_name_input else "UNKNOWN"
                        hs_manager.save_score(final_name, player.score)
                        GAME_STATE = "HIGHSCORES"
                        renderer.screen.fill((0,0,0)) 
                    elif evt.key == pygame.K_BACKSPACE:
                        player_name_input = player_name_input[:-1]
                    else:
                        if len(player_name_input) < 8 and evt.unicode.isalpha():
                            player_name_input += evt.unicode.upper()

            blink_cursor += 1
            cursor = "_" if (blink_cursor // 30) % 2 == 0 else " "
            display_text = " ".join(list(player_name_input)) + cursor
            input_surf = font_gameover.render(display_text, True, (255, 255, 255))
            renderer.screen.blit(input_surf, input_surf.get_rect(center=(SCREEN_WIDTH//2, 350)))
            hint = font_sign.render("(MAX 8 LETRAS - ENTER PARA CONFIRMAR)", True, (100, 100, 100))
            renderer.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, 500)))
            renderer.render_step()

        elif GAME_STATE == "HIGHSCORES":
            renderer.screen.fill((10, 10, 20))
            hs_manager.draw_table(renderer, font_gameover, font_score)
            if input_sys.was_key_just_pressed(pygame.K_RETURN) or input_sys.was_key_just_pressed(pygame.K_ESCAPE):
                GAME_STATE = "MENU"
                title_screen.reset()
                renderer.screen.fill((0,0,0)) 
            renderer.render_step()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()