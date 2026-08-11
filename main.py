import asyncio
import math
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pygame

# Graceful fallback for web deployment where OpenCV/MediaPipe isn't available
try:
    from gesture_controller import HandController

    HAS_GESTURE = True
except Exception:
    HAS_GESTURE = False

from obstacles import Building, EnergyCore, Fireball, PowerUp
from player import Player
from settings import *

TOTAL_TIME_LIMIT = 100.0  # 100 Seconds Limit
MAX_LIVES = 3


class ParallaxBackground:
    """Renders environment backgrounds that change based on progress time."""

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.stars = [
            [
                random.randint(0, width),
                random.randint(0, height),
                random.uniform(0.5, 2.5),
            ]
            for _ in range(80)
        ]

        self.buildings_far = []
        x = 0
        while x < width + 100:
            w = random.randint(40, 90)
            h = random.randint(100, 260)
            self.buildings_far.append({"x": x, "w": w, "h": h})
            x += w + random.randint(10, 30)

    def update(self, dt, speed_mult):
        for star in self.stars:
            star[0] -= 40 * star[2] * speed_mult * dt
            if star[0] < 0:
                star[0] = self.width
                star[1] = random.randint(0, self.height)

        for bldg in self.buildings_far:
            bldg["x"] -= 80 * speed_mult * dt

        if (
            self.buildings_far
            and self.buildings_far[0]["x"] + self.buildings_far[0]["w"] < 0
        ):
            last_x = (
                self.buildings_far[-1]["x"] + self.buildings_far[-1]["w"]
            )
            w = random.randint(40, 90)
            h = random.randint(100, 260)
            self.buildings_far.pop(0)
            self.buildings_far.append(
                {"x": last_x + random.randint(10, 30), "w": w, "h": h}
            )

    def draw(self, surface, elapsed_time, is_ignited):
        if elapsed_time < 35:
            bg_color = (15, 10, 30) if is_ignited else (10, 15, 30)
            far_bldg_color = (25, 30, 50)
            horizon_glow = (0, 120, 255, 40)
            zone_name = "ZONE 1: NIGHT CITY"
        elif elapsed_time < 70:
            bg_color = (35, 10, 25) if is_ignited else (25, 10, 35)
            far_bldg_color = (55, 20, 50)
            horizon_glow = (255, 80, 0, 50)
            zone_name = "ZONE 2: CYBER GRID"
        else:
            bg_color = (25, 5, 15) if is_ignited else (5, 5, 18)
            far_bldg_color = (20, 15, 35)
            horizon_glow = (0, 200, 255, 60)
            zone_name = "ZONE 3: STRATOSPHERE EDGE"

        surface.fill(bg_color)

        glow_surf = pygame.Surface((self.width, 150), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, horizon_glow, (0, 0, self.width, 150))
        surface.blit(glow_surf, (0, self.height - 150))

        for star in self.stars:
            color = (
                (255, 255, 200) if elapsed_time >= 70 else (180, 210, 255)
            )
            pygame.draw.circle(
                surface, color, (int(star[0]), int(star[1])), int(star[2])
            )

        if elapsed_time < 70:
            for bldg in self.buildings_far:
                rect = (bldg["x"], self.height - bldg["h"], bldg["w"], bldg["h"])
                pygame.draw.rect(surface, far_bldg_color, rect)
                if elapsed_time >= 35:
                    for wy in range(
                        self.height - bldg["h"] + 10, self.height - 10, 25
                    ):
                        pygame.draw.rect(
                            surface, (255, 0, 120), (bldg["x"] + 8, wy, 4, 8)
                        )

        if 35 <= elapsed_time < 70:
            grid_y = self.height - 40
            pygame.draw.line(
                surface, (255, 0, 150), (0, grid_y), (self.width, grid_y), 2
            )

        if elapsed_time >= 70:
            pygame.draw.arc(
                surface,
                (0, 180, 255),
                (-100, self.height - 80, self.width + 200, 200),
                0,
                math.pi,
                4,
            )

        return zone_name


class BluePoint(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_mult=1.0):
        super().__init__()
        self.image = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 150, 255, 120), (9, 9), 9)
        pygame.draw.circle(self.image, (0, 210, 255), (9, 9), 6)
        pygame.draw.circle(self.image, (255, 255, 255), (9, 9), 3)

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 220 * speed_mult

    def update(self, dt):
        self.rect.x -= int(self.speed * dt)
        if self.rect.right < 0:
            self.kill()


class Game:

    def __init__(self):
        pygame.init()
        pygame.font.init()
        try:
            pygame.mixer.init()
        except Exception:
            pass

        # Using SCALED flags enables browser canvas scaling in Pygbag
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
        pygame.display.set_caption("IRONFLUX")
        self.clock = pygame.time.Clock()

        self.gesture_ctrl = None
        if HAS_GESTURE:
            try:
                self.gesture_ctrl = HandController(WIDTH, HEIGHT)
            except Exception:
                self.gesture_ctrl = None

        self.background_mgr = ParallaxBackground(WIDTH, HEIGHT)

        self.score = 0
        self.lives = MAX_LIVES
        self.invincible_timer = 0.0
        self.elapsed_time = 0.0
        self.speed_multiplier = 1.0
        self.final_survival_time = 0

        self.gameover_img = self.create_arc_reactor_surface(200)
        self.fullbody_ironman_img = self.create_fullbody_ironman_surface(
            140, 310
        )

        self.state = "START"
        self.running = True

        self.start_btn_rect = pygame.Rect(
            WIDTH // 2 - 100, HEIGHT - 75, 200, 50
        )
        self.reset_game()

    def create_arc_reactor_surface(self, size):
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size // 2, size // 2)

        pygame.draw.circle(surf, (160, 165, 175), center, size // 2)
        pygame.draw.circle(surf, (80, 85, 95), center, size // 2 - 6)
        pygame.draw.circle(surf, (140, 40, 45), center, size // 2 - 18)
        pygame.draw.circle(surf, (200, 205, 215), center, size // 2 - 32)
        pygame.draw.circle(surf, (40, 45, 55), center, size // 2 - 46)

        pygame.draw.circle(surf, (0, 180, 255, 180), center, size // 2 - 58)
        pygame.draw.circle(surf, (0, 220, 255), center, size // 2 - 68)
        pygame.draw.circle(surf, (255, 255, 255), center, size // 2 - 78)

        num_segments = 12
        for i in range(num_segments):
            angle = i * (2 * math.pi / num_segments)
            x1 = center[0] + int(math.cos(angle) * (size // 2 - 46))
            y1 = center[1] + int(math.sin(angle) * (size // 2 - 46))
            x2 = center[0] + int(math.cos(angle) * (size // 2 - 6))
            y2 = center[1] + int(math.sin(angle) * (size // 2 - 6))
            pygame.draw.line(surf, (30, 35, 40), (x1, y1), (x2, y2), 3)

        return surf

    def create_fullbody_ironman_surface(self, w, h):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx = w // 2

        pygame.draw.ellipse(surf, (0, 200, 255, 60), (cx - 45, h - 22, 90, 18))
        pygame.draw.ellipse(
            surf, (0, 240, 255, 120), (cx - 25, h - 18, 50, 10)
        )

        DARK_RED = (120, 10, 20)
        ARMOR_RED = (185, 20, 30)
        GOLD_DARK = (180, 130, 20)
        GOLD_BRIGHT = (240, 190, 40)
        SILVER_TRIM = (190, 200, 210)
        ARC_BLUE = (0, 230, 255)
        WHITE = (255, 255, 255)

        pygame.draw.polygon(
            surf,
            DARK_RED,
            [
                (cx - 35, h - 70),
                (cx - 15, h - 70),
                (cx - 12, h - 10),
                (cx - 40, h - 10),
            ],
        )
        pygame.draw.polygon(
            surf,
            DARK_RED,
            [
                (cx + 15, h - 70),
                (cx + 35, h - 70),
                (cx + 40, h - 10),
                (cx + 12, h - 10),
            ],
        )
        pygame.draw.polygon(
            surf,
            ARMOR_RED,
            [
                (cx - 32, h - 65),
                (cx - 18, h - 65),
                (cx - 15, h - 12),
                (cx - 36, h - 12),
            ],
        )
        pygame.draw.polygon(
            surf,
            ARMOR_RED,
            [
                (cx + 18, h - 65),
                (cx + 32, h - 65),
                (cx + 36, h - 12),
                (cx + 15, h - 12),
            ],
        )

        pygame.draw.polygon(
            surf,
            GOLD_BRIGHT,
            [
                (cx - 32, h - 75),
                (cx - 16, h - 75),
                (cx - 18, h - 60),
                (cx - 30, h - 60),
            ],
        )
        pygame.draw.polygon(
            surf,
            GOLD_BRIGHT,
            [
                (cx + 16, h - 75),
                (cx + 32, h - 75),
                (cx + 30, h - 60),
                (cx + 18, h - 60),
            ],
        )

        pygame.draw.polygon(
            surf,
            GOLD_DARK,
            [
                (cx - 30, h - 140),
                (cx - 12, h - 140),
                (cx - 14, h - 75),
                (cx - 32, h - 75),
            ],
        )
        pygame.draw.polygon(
            surf,
            GOLD_DARK,
            [
                (cx + 12, h - 140),
                (cx + 30, h - 140),
                (cx + 32, h - 75),
                (cx + 14, h - 75),
            ],
        )

        pygame.draw.polygon(
            surf,
            DARK_RED,
            [
                (cx - 38, h - 230),
                (cx + 38, h - 230),
                (cx + 25, h - 135),
                (cx - 25, h - 135),
            ],
        )
        pygame.draw.polygon(
            surf,
            ARMOR_RED,
            [
                (cx - 34, h - 225),
                (cx + 34, h - 225),
                (cx + 22, h - 140),
                (cx - 22, h - 140),
            ],
        )

        for y_off in [155, 172, 189]:
            pygame.draw.polygon(
                surf,
                GOLD_BRIGHT,
                [
                    (cx - 18, h - y_off),
                    (cx + 18, h - y_off),
                    (cx + 15, h - y_off + 10),
                    (cx - 15, h - y_off + 10),
                ],
            )

        pygame.draw.ellipse(surf, ARMOR_RED, (cx - 58, h - 240, 32, 22))
        pygame.draw.ellipse(surf, ARMOR_RED, (cx + 26, h - 240, 32, 22))
        pygame.draw.ellipse(
            surf, SILVER_TRIM, (cx - 54, h - 236, 24, 14), width=2
        )
        pygame.draw.ellipse(
            surf, SILVER_TRIM, (cx + 30, h - 236, 24, 14), width=2
        )

        pygame.draw.polygon(
            surf,
            ARMOR_RED,
            [
                (cx - 52, h - 220),
                (cx - 36, h - 220),
                (cx - 42, h - 160),
                (cx - 56, h - 160),
            ],
        )
        pygame.draw.polygon(
            surf,
            ARMOR_RED,
            [
                (cx + 36, h - 220),
                (cx + 52, h - 220),
                (cx + 56, h - 160),
                (cx + 42, h - 160),
            ],
        )
        pygame.draw.polygon(
            surf,
            GOLD_BRIGHT,
            [
                (cx - 55, h - 160),
                (cx - 41, h - 160),
                (cx - 46, h - 120),
                (cx - 58, h - 120),
            ],
        )
        pygame.draw.polygon(
            surf,
            GOLD_BRIGHT,
            [
                (cx + 41, h - 160),
                (cx + 55, h - 160),
                (cx + 58, h - 120),
                (cx + 46, h - 120),
            ],
        )

        pygame.draw.polygon(
            surf,
            ARC_BLUE,
            [(cx, h - 200), (cx - 14, h - 216), (cx + 14, h - 216)],
        )
        pygame.draw.polygon(
            surf, WHITE, [(cx, h - 202), (cx - 9, h - 214), (cx + 9, h - 214)]
        )
        pygame.draw.polygon(
            surf,
            SILVER_TRIM,
            [(cx, h - 197), (cx - 17, h - 219), (cx + 17, h - 219)],
            width=2,
        )

        pygame.draw.ellipse(surf, DARK_RED, (cx - 22, h - 280, 44, 48))
        pygame.draw.polygon(
            surf,
            GOLD_BRIGHT,
            [
                (cx - 16, h - 272),
                (cx + 16, h - 272),
                (cx + 18, h - 252),
                (cx + 10, h - 238),
                (cx - 10, h - 238),
                (cx - 18, h - 252),
            ],
        )
        pygame.draw.line(surf, DARK_RED, (cx - 16, h - 264), (cx + 16, h - 264), 2)

        pygame.draw.line(surf, ARC_BLUE, (cx - 12, h - 258), (cx - 4, h - 258), 3)
        pygame.draw.line(surf, ARC_BLUE, (cx + 4, h - 258), (cx + 12, h - 258), 3)
        pygame.draw.line(surf, WHITE, (cx - 10, h - 258), (cx - 6, h - 258), 1)
        pygame.draw.line(surf, WHITE, (cx + 6, h - 258), (cx + 10, h - 258), 1)

        return surf

    def reset_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()

        self.player = Player(100, HEIGHT // 2)
        self.all_sprites.add(self.player)

        self.score = 0
        self.lives = MAX_LIVES
        self.invincible_timer = 0.0
        self.elapsed_time = 0.0
        self.speed_multiplier = 1.0
        self.final_survival_time = 0
        self.spawn_timer = 0.0
        self.building_timer = 0.0

    def spawn_entities(self, dt):
        self.spawn_timer += dt * self.speed_multiplier
        self.building_timer += dt * self.speed_multiplier

        if self.spawn_timer >= 0.7:
            self.spawn_timer = 0.0

            fb = Fireball(WIDTH + 30, random.randint(40, HEIGHT - 180))
            if hasattr(fb, "speed"):
                fb.speed *= self.speed_multiplier
            self.all_sprites.add(fb)
            self.obstacles.add(fb)

            rand_val = random.random()
            if rand_val < 0.60:
                blue_pt = BluePoint(
                    WIDTH + 30,
                    random.randint(40, HEIGHT - 180),
                    self.speed_multiplier,
                )
                self.all_sprites.add(blue_pt)
                self.collectibles.add(blue_pt)
            elif rand_val < 0.85:
                core = EnergyCore(WIDTH + 30, random.randint(40, HEIGHT - 180))
                if hasattr(core, "speed"):
                    core.speed *= self.speed_multiplier
                self.all_sprites.add(core)
                self.collectibles.add(core)
            else:
                pup = PowerUp(
                    WIDTH + 30, random.randint(40, HEIGHT - 180), "hyper"
                )
                if hasattr(pup, "speed"):
                    pup.speed *= self.speed_multiplier
                self.all_sprites.add(pup)
                self.collectibles.add(pup)

        if self.building_timer >= 2.5 and self.elapsed_time < 70:
            self.building_timer = 0.0
            is_big = random.choice([True, False])
            bldg = Building(WIDTH + 20, is_big=is_big)
            if hasattr(bldg, "speed"):
                bldg.speed *= self.speed_multiplier
            self.all_sprites.add(bldg)
            self.obstacles.add(bldg)

    def handle_collisions(self):
        collected = pygame.sprite.spritecollide(
            self.player, self.collectibles, True
        )
        multiplier = 2 if self.player.is_ignited else 1

        for item in collected:
            if isinstance(item, BluePoint):
                self.score += 2 * multiplier
            elif isinstance(item, EnergyCore):
                self.score += 50 * multiplier
            elif isinstance(item, PowerUp):
                self.player.activate_ignite(6.0)
                self.score += 200 * multiplier

        if not self.player.is_ignited and self.invincible_timer <= 0:
            hit_obstacles = pygame.sprite.spritecollide(
                self.player, self.obstacles, True
            )
            if hit_obstacles:
                self.lives -= 1
                self.invincible_timer = 1.5
                if self.lives <= 0:
                    self.end_round(is_victory=False)

    def end_round(self, is_victory=False):
        self.final_survival_time = int(self.elapsed_time)
        self.state = "VICTORY" if is_victory else "GAMEOVER"

    def draw_start_page(self):
        self.screen.fill((10, 12, 20))

        font_title = pygame.font.SysFont("Consolas", 46, bold=True)
        txt_title = font_title.render("IRONFLUX", True, (255, 50, 60))
        self.screen.blit(txt_title, (WIDTH // 2 - txt_title.get_width() // 2, 15))

        box_w, box_h = WIDTH - 60, HEIGHT - 110
        rules_box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        rules_box.fill((20, 25, 40, 220))
        pygame.draw.rect(
            rules_box, (0, 200, 255), (0, 0, box_w, box_h), 2, border_radius=10
        )
        self.screen.blit(rules_box, (30, 70))

        font_head = pygame.font.SysFont("Consolas", 20, bold=True)
        font_text = pygame.font.SysFont("Consolas", 14)

        txt_head = font_head.render(
            "MISSION RULES & CONTROLS", True, (0, 240, 255)
        )
        self.screen.blit(
            txt_head, (WIDTH // 2 - txt_head.get_width() // 2, 82)
        )

        self.screen.blit(self.fullbody_ironman_img, (WIDTH - 180, HEIGHT - 380))

        rules = [
            ("CONTROLS:", (255, 215, 0)),
            ("  - WASD / Arrow Keys or Mouse to move.", (220, 220, 220)),
            ("  - Press SHIFT to activate Ignite Mode.", (220, 220, 220)),
            ("  - Press F or F11 to Toggle Fullscreen.", (0, 220, 255)),
            ("STAGES & OBJECTIVE:", (255, 215, 0)),
            (
                "  - Survive 100s across 3 unique Environments!",
                (220, 220, 220),
            ),
            (
                "  - Zone 1: Night City | Zone 2: Cyber Grid | Zone 3:"
                " Atmosphere",
                (220, 220, 220),
            ),
            ("LIVES SYSTEM:", (255, 60, 80)),
            (
                "  - You have 3 Lives! Obstacles drain 1 life + grant 1.5s"
                " i-frames.",
                (220, 220, 220),
            ),
            ("SCORING SYSTEM:", (0, 255, 150)),
            (
                "  - Blue Orbs: +2 pts  |  Energy Cores: +50 pts",
                (220, 220, 220),
            ),
            ("  - Power-Ups: +200 pts (Triggers 6s Ignite)", (220, 220, 220)),
            ("IGNITE MODE:", (255, 140, 0)),
            (
                "  - Invincible to obstacles + DOUBLE POINTS (2x)!",
                (220, 220, 220),
            ),
        ]

        y_offset = 105
        for line, color in rules:
            txt_line = font_text.render(line, True, color)
            self.screen.blit(txt_line, (45, y_offset))
            y_offset += 20

        mouse_pos = pygame.mouse.get_pos()
        btn_color = (
            (255, 70, 0)
            if self.start_btn_rect.collidepoint(mouse_pos)
            else (200, 40, 40)
        )

        pygame.draw.rect(
            self.screen, btn_color, self.start_btn_rect, border_radius=12
        )
        pygame.draw.rect(
            self.screen, (255, 215, 0), self.start_btn_rect, 3, border_radius=12
        )

        font_btn = pygame.font.SysFont("Consolas", 22, bold=True)
        txt_btn = font_btn.render("START GAME", True, (255, 255, 255))
        self.screen.blit(
            txt_btn,
            (
                self.start_btn_rect.centerx - txt_btn.get_width() // 2,
                self.start_btn_rect.centery - txt_btn.get_height() // 2,
            ),
        )

    def draw_game_over(self, is_victory=False):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 210))
        self.screen.blit(overlay, (0, 0))

        font_large = pygame.font.SysFont("Consolas", 36, bold=True)
        font_small = pygame.font.SysFont("Consolas", 22, bold=True)

        if is_victory:
            title_text = "MISSION COMPLETE: SURVIVED 100s!"
            title_color = (0, 255, 150)
        else:
            title_text = "SYSTEM CRITICAL: GAME OVER"
            title_color = (255, 60, 80)

        img_rect = self.gameover_img.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 - 10)
        )
        self.screen.blit(self.gameover_img, img_rect)

        time_str = f"TIME SURVIVED: {self.final_survival_time}s / 100s"

        txt_title = font_large.render(title_text, True, title_color)
        txt_time = font_small.render(time_str, True, (0, 220, 255))
        txt_score = font_small.render(
            f"FINAL SCORE: {int(self.score)}", True, (255, 255, 255)
        )
        txt_restart = font_small.render(
            "Press SPACE to Play Again", True, (180, 180, 180)
        )

        self.screen.blit(
            txt_title,
            (WIDTH // 2 - txt_title.get_width() // 2, HEIGHT // 2 - 140),
        )
        self.screen.blit(
            txt_time, (WIDTH // 2 - txt_time.get_width() // 2, HEIGHT // 2 + 100)
        )
        self.screen.blit(
            txt_score,
            (WIDTH // 2 - txt_score.get_width() // 2, HEIGHT // 2 + 130),
        )
        self.screen.blit(
            txt_restart,
            (WIDTH // 2 - txt_restart.get_width() // 2, HEIGHT // 2 + 170),
        )

    async def run(self):
        while self.running:
            dt = min(self.clock.tick(60) / 1000.0, 0.1)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if (
                        self.state == "START"
                        and self.start_btn_rect.collidepoint(event.pos)
                    ):
                        self.reset_game()
                        self.state = "PLAYING"
                elif event.type == pygame.KEYDOWN:
                    # Fullscreen toggle on 'F' or 'F11'
                    if event.key in (pygame.K_f, pygame.K_F11):
                        pygame.display.toggle_fullscreen()
                    elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                        if self.state == "PLAYING":
                            self.player.activate_ignite(5.0)
                    elif event.key == pygame.K_SPACE and self.state in [
                        "GAMEOVER",
                        "VICTORY",
                    ]:
                        self.reset_game()
                        self.state = "PLAYING"

            target_y = pygame.mouse.get_pos()[1]
            hand_active = False

            if self.gesture_ctrl:
                try:
                    self.gesture_ctrl.update()
                    if hasattr(self.gesture_ctrl, "hand_detected") and self.gesture_ctrl.hand_detected:
                        target_y = self.gesture_ctrl.target_y
                        hand_active = True
                except Exception:
                    pass

            if self.state == "START":
                self.draw_start_page()
            elif self.state == "PLAYING":
                self.elapsed_time += dt

                if self.invincible_timer > 0:
                    self.invincible_timer -= dt

                self.speed_multiplier = 1.0 + (
                    int(self.elapsed_time // 5) * 0.10
                )

                if self.elapsed_time >= TOTAL_TIME_LIMIT:
                    self.elapsed_time = TOTAL_TIME_LIMIT
                    self.end_round(is_victory=True)

                self.background_mgr.update(dt, self.speed_multiplier)
                zone_title = self.background_mgr.draw(
                    self.screen, self.elapsed_time, self.player.is_ignited
                )

                self.spawn_entities(dt)
                self.player.update(
                    dt, target_y, hand_active=hand_active
                )
                self.obstacles.update(dt)
                self.collectibles.update(dt)

                self.handle_collisions()

                if (
                    self.invincible_timer <= 0
                    or int(self.invincible_timer * 12) % 2 == 0
                ):
                    self.all_sprites.draw(self.screen)

                if self.gesture_ctrl and hasattr(self.gesture_ctrl, "draw_preview"):
                    try:
                        self.gesture_ctrl.draw_preview(self.screen)
                    except Exception:
                        pass

                font_hud = pygame.font.SysFont("Consolas", 18, bold=True)

                current_sec = int(self.elapsed_time)
                time_txt = font_hud.render(
                    f"TIME: {current_sec}s / 100s", True, (0, 220, 255)
                )
                score_txt = font_hud.render(
                    f"SCORE: {int(self.score)}", True, (255, 255, 255)
                )
                speed_txt = font_hud.render(
                    f"SPEED: {self.speed_multiplier:.2f}x", True, (255, 215, 0)
                )
                zone_txt = font_hud.render(zone_title, True, (0, 255, 180))

                lives_str = "LIVES: " + ("♥ " * self.lives)
                lives_txt = font_hud.render(lives_str, True, (255, 60, 80))

                self.screen.blit(lives_txt, (20, 15))
                self.screen.blit(zone_txt, (20, 38))

                self.screen.blit(time_txt, (WIDTH - 180, 15))
                self.screen.blit(score_txt, (WIDTH - 180, 38))
                self.screen.blit(speed_txt, (WIDTH - 180, 61))

                if self.player.is_ignited:
                    ignite_font = pygame.font.SysFont("Consolas", 16, bold=True)
                    ignite_txt = ignite_font.render(
                        f"IGNITE MODE: {self.player.ignite_timer:.1f}s",
                        True,
                        (255, 140, 0),
                    )
                    self.screen.blit(ignite_txt, (180, 18))

            elif self.state in ["GAMEOVER", "VICTORY"]:
                self.draw_game_over(is_victory=(self.state == "VICTORY"))

            pygame.display.flip()
            await asyncio.sleep(0)

        if self.gesture_ctrl and hasattr(self.gesture_ctrl, "release"):
            try:
                self.gesture_ctrl.release()
            except Exception:
                pass
        pygame.quit()


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())