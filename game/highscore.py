import json
import os
import pygame

class HighScoreManager:
    def __init__(self, filename="scores.json"):
        self.filename = filename
        self.scores = self.load_scores()

    def load_scores(self):
        if not os.path.exists(self.filename):
            return [
                {"name": "JATOBA", "score": 5000},
                {"name": "DEV",    "score": 3000},
                {"name": "PLAYER", "score": 1000}
            ]
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except:
            return []

    def save_score(self, name, score):
        self.scores.append({"name": name, "score": score})
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        # Limita ao Top 5 ---
        self.scores = self.scores[:5]
        # ---------------------------------
        
        with open(self.filename, 'w') as f:
            json.dump(self.scores, f)

    def draw_table(self, renderer, font_title, font_list):
        sw, sh = renderer.width, renderer.height
        cx = sw // 2
        
        title = font_title.render("TOP 5 JOGADORES", True, (255, 215, 0))
        renderer.screen.blit(title, title.get_rect(center=(cx, 100)))
        
        header = font_list.render("RANK   NAME       SCORE", True, (100, 100, 255))
        renderer.screen.blit(header, header.get_rect(center=(cx, 180)))
        
        y = 230
        for i, entry in enumerate(self.scores):
            color = (255, 255, 255)
            if i == 0: color = (255, 255, 0)
            elif i == 1: color = (200, 200, 200)
            elif i == 2: color = (205, 127, 50)
            
            rank_str = f"{i+1}."
            name_str = entry['name']
            score_str = f"{entry['score']:06d}"
            
            r_surf = font_list.render(rank_str, True, color)
            renderer.screen.blit(r_surf, (cx - 150, y))
            
            n_surf = font_list.render(name_str, True, color)
            renderer.screen.blit(n_surf, (cx - 80, y))
            
            s_surf = font_list.render(score_str, True, color)
            renderer.screen.blit(s_surf, (cx + 80, y))
            
            y += 45 # Aumentei um pouco o espaçamento já que são menos itens

        footer = font_list.render("PRESS ENTER TO MENU", True, (100, 100, 100))
        renderer.screen.blit(footer, footer.get_rect(center=(cx, sh - 50)))