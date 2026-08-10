import pygame
import math
from settings import *

class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont("monospace", 18, bold=True)
        self.small_font = pygame.font.SysFont("monospace", 14, bold=True)
        self.title_font = pygame.font.SysFont("monospace", 36, bold=True)
        
        # Animation & Pulse trackers
        self.pulse_timer = 0
        self.warning_alpha = 0
        self.warning_dir = 1

    def draw(self, surface, player, score, distance, combo, high_score, current_level):
        self.pulse_timer += 0.08
        pulse_scale = math.sin(self.pulse_timer)
        
        # --- 1. HUD BACKGROUND BAR WITH TECH BORDER ---
        hud_height = 70
        hud_y = HEIGHT - hud_height
        
        hud_bg = pygame.Surface((WIDTH, hud_height), pygame.SRCALPHA)
        hud_bg.fill((5, 12, 25, 210))  # Semi-transparent dark cyan/blue
        surface.blit(hud_bg, (0, hud_y))

        # Top cyan glowing border line
        pygame.draw.line(surface, COLOR_CYAN, (0, hud_y), (WIDTH, hud_y), 2)
        pygame.draw.line(surface, (0, 240, 255, 80), (0, hud_y + 2), (WIDTH, hud_y + 2), 1)

        # --- 2. LIVES DISPLAY (Heart / Suit Icons) ---
        lives_label = self.small_font.render("SUIT INTEGRITY", True, (180, 200, 220))
        surface.blit(lives_label, (20, hud_y + 8))
        
        # Animated heart color or visual icon
        lives_str = "❤️ " * player.lives if player.lives > 0 else "CRITICAL"
        lives_color = COLOR_RED if player.lives <= 1 else COLOR_WHITE
        lives_txt = self.font.render(lives_str, True, lives_color)
        surface.blit(lives_txt, (20, hud_y + 28))

        # --- 3. DYNAMIC ENERGY BAR (Flashes RED when Low) ---
        energy_x, energy_y, bar_w, bar_h = 190, hud_y + 30, 140, 18
        
        # Energy Label
        eng_label = self.small_font.render("ARC ENERGY", True, (180, 200, 220))
        surface.blit(eng_label, (energy_x, hud_y + 8))
        
        # Outer Frame
        pygame.draw.rect(surface, COLOR_DARK_GRAY, (energy_x, energy_y, bar_w, bar_h), border_radius=4)
        
        # Energy Fill & Warning Color
        energy_pct = max(0, player.energy / MAX_ENERGY)
        energy_fill_w = int(energy_pct * bar_w)
        
        if energy_pct < 0.25:
            # Low energy flashing effect
            flash = abs(math.sin(self.pulse_timer * 2))
            energy_color = (255, int(50 * flash), int(50 * flash))
        else:
            energy_color = COLOR_CYAN

        if energy_fill_w > 0:
            pygame.draw.rect(surface, energy_color, (energy_x, energy_y, energy_fill_w, bar_h), border_radius=4)
        
        # Inner Gloss Highlight Line
        pygame.draw.line(surface, (255, 255, 255, 120), (energy_x + 2, energy_y + 3), (energy_x + bar_w - 2, energy_y + 3), 1)
        pygame.draw.rect(surface, COLOR_CYAN, (energy_x, energy_y, bar_w, bar_h), 1, border_radius=4)

        # --- 4. THRUSTER BOOST BAR ---
        boost_x, boost_y = 360, hud_y + 30
        
        boost_label = self.small_font.render("THRUSTERS", True, (180, 200, 220))
        surface.blit(boost_label, (boost_x, hud_y + 8))
        
        pygame.draw.rect(surface, COLOR_DARK_GRAY, (boost_x, boost_y, bar_w, bar_h), border_radius=4)
        
        boost_pct = max(0, player.boost / MAX_BOOST)
        boost_fill_w = int(boost_pct * bar_w)
        
        if boost_fill_w > 0:
            pygame.draw.rect(surface, COLOR_GOLD, (boost_x, boost_y, boost_fill_w, bar_h), border_radius=4)
            
        pygame.draw.line(surface, (255, 255, 255, 120), (boost_x + 2, boost_y + 3), (boost_x + bar_w - 2, boost_y + 3), 1)
        pygame.draw.rect(surface, COLOR_GOLD, (boost_x, boost_y, bar_w, bar_h), 1, border_radius=4)

        # --- 5. STATS & COMBO MULTIPLIER (Pulsing Combo Text) ---
        score_txt = self.font.render(f"SCORE: {score:06d}", True, COLOR_GOLD)
        dist_txt = self.font.render(f"DIST: {int(distance)}m", True, COLOR_WHITE)
        level_txt = self.small_font.render(f"ZONE: {current_level}", True, COLOR_CYAN)

        surface.blit(score_txt, (530, hud_y + 12))
        surface.blit(dist_txt, (530, hud_y + 38))
        surface.blit(level_txt, (710, hud_y + 40))

        # Dynamic Combo Pulse (Scales and changes color when combo > 1)
        if combo > 1:
            combo_color = (255, 215, 0) if combo < 5 else (255, 80, 0)
            combo_surface = self.font.render(f"COMBO x{combo}!", True, combo_color)
            
            # Subtle bounce effect
            offset_y = int(pulse_scale * 3)
            surface.blit(combo_surface, (710, hud_y + 12 + offset_y))
        else:
            combo_txt = self.small_font.render("COMBO: x1", True, (150, 150, 150))
            surface.blit(combo_txt, (710, hud_y + 14))

    def draw_game_over(self, surface, final_score, distance, high_score):
        # Semi-transparent Vignette Overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 0, 5, 230))
        surface.blit(overlay, (0, 0))

        # Red Critical Glow Box
        box_rect = pygame.Rect(WIDTH // 2 - 250, 120, 500, 340)
        pygame.draw.rect(surface, (20, 5, 10), box_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_RED, box_rect, width=2, border_radius=12)

        # Flashing Warning Line
        self.warning_alpha += 4 * self.warning_dir
        if self.warning_alpha >= 255 or self.warning_alpha <= 50:
            self.warning_dir *= -1
            
        warn_color = (255, 30, 30, max(50, min(255, self.warning_alpha)))
        
        # Render Text Elements
        t1 = self.title_font.render("SYSTEM CRITICAL", True, warn_color)
        t_sub = self.font.render("SUIT DESTROYED - MISSION FAILED", True, COLOR_WHITE)
        
        t2 = self.font.render(f"FINAL SCORE   : {final_score}", True, COLOR_GOLD)
        t3 = self.font.render(f"DISTANCE      : {int(distance)}m", True, COLOR_WHITE)
        t4 = self.font.render(f"PERSONAL BEST : {high_score}", True, COLOR_CYAN)
        
        t5 = self.font.render("[ R ] REBOOT SUIT  |  [ Q ] ABORT", True, COLOR_GREEN)

        # Center Text inside the Dialogue Box
        surface.blit(t1, (WIDTH // 2 - t1.get_width() // 2, 145))
        surface.blit(t_sub, (WIDTH // 2 - t_sub.get_width() // 2, 195))
        
        # Separator Line
        pygame.draw.line(surface, COLOR_RED, (WIDTH // 2 - 200, 230), (WIDTH // 2 + 200, 230), 1)

        surface.blit(t2, (WIDTH // 2 - 160, 255))
        surface.blit(t3, (WIDTH // 2 - 160, 290))
        surface.blit(t4, (WIDTH // 2 - 160, 325))
        
        surface.blit(t5, (WIDTH // 2 - t5.get_width() // 2, 395))