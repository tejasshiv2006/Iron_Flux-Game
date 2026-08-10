import os
import zipfile

# Source files with all bug fixes applied
files = {
    "settings.py": '''import pygame

WIDTH = 1000
HEIGHT = 600
FPS = 60

COLOR_BG = (10, 15, 30)
COLOR_WHITE = (255, 255, 255)
COLOR_GOLD = (255, 215, 0)
COLOR_CYAN = (0, 230, 255)
COLOR_BLUE = (0, 120, 255)
COLOR_RED = (255, 50, 50)
COLOR_GREEN = (50, 255, 100)
COLOR_PURPLE = (180, 50, 255)
COLOR_DARK_GRAY = (30, 30, 40)

INITIAL_LIVES = 3
MAX_ENERGY = 100.0
ENERGY_DEPLETION_RATE = 3.5
ENERGY_CORE_RECHARGE = 20.0
MAX_BOOST = 100.0
BOOST_CONSUMPTION_RATE = 40.0
BOOST_RECHARGE_RATE = 15.0

LEVEL_2_DIST = 1000
LEVEL_3_DIST = 2500
LEVEL_4_DIST = 5000

HIGH_SCORE_FILE = "highscore.json"
''',

    "player.py": '''import pygame
import math
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 50
        self.height = 30
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_suit()
        self.rect = self.image.get_rect(center=(x, y))
        
        self.speed = 6
        self.vx = 0
        self.vy = 0
        
        self.lives = INITIAL_LIVES
        self.energy = MAX_ENERGY
        self.boost = MAX_BOOST
        
        self.shield_active = False
        self.shield_timer = 0
        self.shield_uses = 3
        
        self.hyper_boost_active = False
        self.hyper_boost_timer = 0
        
        self.magnet_active = False
        self.magnet_timer = 0
        
        self.invulnerable = False
        self.invuln_timer = 0

    def draw_suit(self):
        self.image.fill((0, 0, 0, 0))
        points = [(0, 15), (35, 0), (50, 15), (35, 30)]
        pygame.draw.polygon(self.image, COLOR_CYAN, points)
        pygame.draw.polygon(self.image, COLOR_WHITE, [(10, 10), (35, 15), (10, 20)])
        pygame.draw.polygon(self.image, COLOR_GOLD, [(0, 10), (-10, 15), (0, 20)])

    def update(self, keys, dt):
        current_time = pygame.time.get_ticks()
        
        if self.shield_active and current_time > self.shield_timer:
            self.shield_active = False
            
        if self.hyper_boost_active and current_time > self.hyper_boost_timer:
            self.hyper_boost_active = False
            
        if self.magnet_active and current_time > self.magnet_timer:
            self.magnet_active = False
            
        if self.invulnerable and current_time > self.invuln_timer:
            self.invulnerable = False

        self.energy -= ENERGY_DEPLETION_RATE * dt
        if self.energy < 0:
            self.energy = 0

        current_speed = self.speed
        if keys[pygame.K_SPACE] and self.boost > 0:
            current_speed *= 1.8
            self.boost -= BOOST_CONSUMPTION_RATE * dt
            if self.boost < 0:
                self.boost = 0
        else:
            self.boost = min(MAX_BOOST, self.boost + BOOST_RECHARGE_RATE * dt)

        if self.hyper_boost_active:
            current_speed *= 2.2

        self.vx = 0
        self.vy = 0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy = -current_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = current_speed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -current_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = current_speed

        self.rect.x += self.vx
        self.rect.y += self.vy
        
        self.rect.left = max(10, self.rect.left)
        self.rect.right = min(WIDTH - 10, self.rect.right)
        self.rect.top = max(10, self.rect.top)
        self.rect.bottom = min(HEIGHT - 70, self.rect.bottom)

    def activate_shield(self):
        if self.shield_uses > 0 and not self.shield_active:
            self.shield_active = True
            self.shield_uses -= 1
            self.shield_timer = pygame.time.get_ticks() + 10000

    def hit(self):
        if self.hyper_boost_active or self.invulnerable:
            return False
            
        if self.shield_active:
            self.shield_active = False
            self.invulnerable = True
            self.invuln_timer = pygame.time.get_ticks() + 1000
            return False

        self.lives -= 1
        self.invulnerable = True
        self.invuln_timer = pygame.time.get_ticks() + 1500
        return True

    def draw_extras(self, surface):
        if self.shield_active:
            pygame.draw.circle(surface, COLOR_CYAN, self.rect.center, 35, 2)
        if self.hyper_boost_active:
            pygame.draw.circle(surface, COLOR_GOLD, self.rect.center, 38, 3)
''',

    "missile.py": '''import pygame
import math
from settings import *

class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y, target):
        super().__init__()
        self.image = pygame.Surface((20, 8), pygame.SRCALPHA)
        pygame.draw.rect(self.image, COLOR_RED, (0, 0, 20, 8), border_radius=3)
        pygame.draw.polygon(self.image, COLOR_GOLD, [(-4, 2), (0, 4), (-4, 6)])
        
        self.rect = self.image.get_rect(center=(x, y))
        self.target = target
        self.speed = 7
        self.tracking_time = pygame.time.get_ticks() + 2000

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        
        if current_time < self.tracking_time and self.target:
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx, dy = dx / dist, dy / dist
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed
        else:
            self.rect.x -= self.speed * 1.2

        if self.rect.right < 0 or self.rect.top > HEIGHT or self.rect.bottom < 0:
            self.kill()
''',

    "ring.py": '''import pygame
from settings import *

class Ring(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.radius = 30
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, COLOR_GOLD, (self.radius, self.radius), self.radius, 4)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self, dt):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()
''',

    "energy_core.py": '''import pygame
import math
from settings import *

class EnergyCore(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, core_type="energy"):
        super().__init__()
        self.type = core_type
        self.radius = 12
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        
        color = COLOR_CYAN if self.type == "energy" else COLOR_PURPLE
        pygame.draw.circle(self.image, color, (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.image, COLOR_WHITE, (self.radius, self.radius), self.radius // 2)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self, dt, player=None):
        if player and player.magnet_active:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist < 250:
                self.rect.x += (dx / dist) * 10
                self.rect.y += (dy / dist) * 10

        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()
''',

    "obstacle.py": '''import pygame
import math
import random
from settings import *

class Drone(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((35, 25), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, COLOR_DARK_GRAY, (0, 0, 35, 25))
        pygame.draw.circle(self.image, COLOR_RED, (17, 12), 5)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.amplitude = random.randint(20, 60)
        self.frequency = random.uniform(0.02, 0.05)
        self.initial_y = y
        self.step = 0

    def update(self, dt):
        self.rect.x -= self.speed
        self.step += 1
        self.rect.y = self.initial_y + math.sin(self.step * self.frequency) * self.amplitude
        if self.rect.right < 0:
            self.kill()

class LaserWall(pygame.sprite.Sprite):
    def __init__(self, x, y, height, speed):
        super().__init__()
        self.image = pygame.Surface((15, height), pygame.SRCALPHA)
        self.image.fill(COLOR_RED)
        pygame.draw.rect(self.image, COLOR_WHITE, (4, 0, 7, height))
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed

    def update(self, dt):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()
''',

    "ui.py": '''import pygame
from settings import *

class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont("monospace", 18, bold=True)
        self.title_font = pygame.font.SysFont("monospace", 36, bold=True)

    def draw(self, surface, player, score, distance, combo, high_score, current_level):
        hud_bg = pygame.Surface((WIDTH, 60))
        hud_bg.set_alpha(180)
        hud_bg.fill((5, 10, 20))
        surface.blit(hud_bg, (0, HEIGHT - 60))

        lives_txt = self.font.render(f"LIVES: {'❤️ ' * player.lives}", True, COLOR_RED)
        surface.blit(lives_txt, (20, HEIGHT - 45))

        pygame.draw.rect(surface, COLOR_DARK_GRAY, (200, HEIGHT - 42, 150, 16), border_radius=4)
        energy_width = max(0, int((player.energy / MAX_ENERGY) * 150))
        pygame.draw.rect(surface, COLOR_CYAN, (200, HEIGHT - 42, energy_width, 16), border_radius=4)
        energy_txt = self.font.render("ENG", True, COLOR_WHITE)
        surface.blit(energy_txt, (155, HEIGHT - 45))

        pygame.draw.rect(surface, COLOR_DARK_GRAY, (430, HEIGHT - 42, 120, 16), border_radius=4)
        boost_width = max(0, int((player.boost / MAX_BOOST) * 120))
        pygame.draw.rect(surface, COLOR_GOLD, (430, HEIGHT - 42, boost_width, 16), border_radius=4)
        boost_txt = self.font.render("BOOST", True, COLOR_WHITE)
        surface.blit(boost_txt, (370, HEIGHT - 45))

        score_txt = self.font.render(f"SCORE: {score}", True, COLOR_GOLD)
        dist_txt = self.font.render(f"DIST: {int(distance)}m", True, COLOR_WHITE)
        combo_txt = self.font.render(f"COMBO: x{combo}", True, COLOR_GREEN if combo > 1 else COLOR_WHITE)
        level_txt = self.font.render(f"ZONE: {current_level}", True, COLOR_CYAN)

        surface.blit(score_txt, (600, HEIGHT - 50))
        surface.blit(dist_txt, (600, HEIGHT - 28))
        surface.blit(combo_txt, (800, HEIGHT - 50))
        surface.blit(level_txt, (800, HEIGHT - 28))

    def draw_game_over(self, surface, final_score, distance, high_score):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        t1 = self.title_font.render("SUIT DESTROYED - MISSION FAILED", True, COLOR_RED)
        t2 = self.font.render(f"Final Score: {final_score}", True, COLOR_GOLD)
        t3 = self.font.render(f"Distance Traveled: {int(distance)} meters", True, COLOR_WHITE)
        t4 = self.font.render(f"High Score: {high_score}", True, COLOR_CYAN)
        t5 = self.font.render("Press 'R' to Restart or 'Q' to Quit", True, COLOR_WHITE)

        surface.blit(t1, (WIDTH // 2 - t1.get_width() // 2, 180))
        surface.blit(t2, (WIDTH // 2 - t2.get_width() // 2, 260))
        surface.blit(t3, (WIDTH // 2 - t3.get_width() // 2, 300))
        surface.blit(t4, (WIDTH // 2 - t4.get_width() // 2, 340))
        surface.blit(t5, (WIDTH // 2 - t5.get_width() // 2, 420))
''',

    "main.py": '''import pygame
import random
import json
import os
import sys

from settings import *
from player import Player
from missile import Missile
from ring import Ring
from energy_core import EnergyCore
from obstacle import Drone, LaserWall
from ui import HUD

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sky Flight Test 🚀")
        self.clock = pygame.time.Clock()

        self.hud = HUD()
        self.high_score = self.load_high_score()
        self.reset_game()

    def load_high_score(self):
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, "r") as f:
                    return json.load(f).get("high_score", 0)
            except Exception:
                return 0
        return 0

    def save_high_score(self):
        with open(HIGH_SCORE_FILE, "w") as f:
            json.dump({"high_score": self.high_score}, f)

    def reset_game(self):
        self.player = Player(100, HEIGHT // 2)
        self.all_sprites = pygame.sprite.Group(self.player)
        
        self.missiles = pygame.sprite.Group()
        self.rings = pygame.sprite.Group()
        self.cores = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()

        self.score = 0
        self.distance = 0.0
        self.combo = 1
        self.game_speed = 5.0
        self.game_over = False

        self.next_ring_spawn = 0
        self.next_core_spawn = 0
        self.next_obstacle_spawn = 0
        self.next_missile_spawn = 0

    def get_current_level(self):
        if self.distance < LEVEL_2_DIST:
            return "1 (Test Zone)"
        elif self.distance < LEVEL_3_DIST:
            return "2 (High Altitude)"
        elif self.distance < LEVEL_4_DIST:
            return "3 (Storm Zone)"
        else:
            return "4 (Combat Sim)"

    def spawn_objects(self, now):
        level = self.get_current_level()

        if now > self.next_ring_spawn:
            ring = Ring(WIDTH + 40, random.randint(50, HEIGHT - 120), self.game_speed)
            self.rings.add(ring)
            self.all_sprites.add(ring)
            self.next_ring_spawn = now + random.randint(1500, 3000)

        if now > self.next_core_spawn:
            core_type = "powerup" if random.random() < 0.2 else "energy"
            core = EnergyCore(WIDTH + 20, random.randint(50, HEIGHT - 120), self.game_speed, core_type)
            self.cores.add(core)
            self.all_sprites.add(core)
            self.next_core_spawn = now + random.randint(2000, 4000)

        if now > self.next_obstacle_spawn:
            if "1" in level:
                drone = Drone(WIDTH + 30, random.randint(50, HEIGHT - 120), self.game_speed * 0.8)
                self.obstacles.add(drone)
                self.all_sprites.add(drone)
            else:
                if random.random() < 0.5:
                    wall_h = random.randint(100, 220)
                    wall_y = random.randint(50, HEIGHT - 120 - wall_h)
                    wall = LaserWall(WIDTH + 30, wall_y, wall_h, self.game_speed)
                    self.obstacles.add(wall)
                    self.all_sprites.add(wall)
                else:
                    drone = Drone(WIDTH + 30, random.randint(50, HEIGHT - 120), self.game_speed * 1.1)
                    self.obstacles.add(drone)
                    self.all_sprites.add(drone)
            
            self.next_obstacle_spawn = now + random.randint(2000, 4500)

        if "1" not in level and now > self.next_missile_spawn:
            missile = Missile(WIDTH + 20, random.randint(50, HEIGHT - 120), self.player)
            self.missiles.add(missile)
            self.all_sprites.add(missile)
            spawn_delay = 3000 if "2" in level else 1800
            self.next_missile_spawn = now + random.randint(spawn_delay, spawn_delay + 2000)

    def handle_collisions(self):
        ring_hits = pygame.sprite.spritecollide(self.player, self.rings, True)
        for _ in ring_hits:
            self.score += 100 * self.combo
            self.combo = min(5, self.combo + 1)

        core_hits = pygame.sprite.spritecollide(self.player, self.cores, True)
        for core in core_hits:
            if core.type == "energy":
                self.player.energy = min(MAX_ENERGY, self.player.energy + ENERGY_CORE_RECHARGE)
                self.score += 50
            else:
                power = random.choice(["magnet", "hyper"])
                if power == "magnet":
                    self.player.magnet_active = True
                    self.player.magnet_timer = pygame.time.get_ticks() + 8000
                else:
                    self.player.hyper_boost_active = True
                    self.player.hyper_boost_timer = pygame.time.get_ticks() + 5000

        hazard_hits = pygame.sprite.spritecollide(self.player, self.obstacles, True) + \\
                      pygame.sprite.spritecollide(self.player, self.missiles, True)
        for _ in hazard_hits:
            self.player.hit()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            now = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_high_score()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        self.player.activate_shield()
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_q:
                            self.save_high_score()
                            pygame.quit()
                            sys.exit()

            if not self.game_over:
                keys = pygame.key.get_pressed()
                self.player.update(keys, dt)

                self.distance += self.game_speed * dt * 10
                self.game_speed = 5.0 + (self.distance / 1000.0)
                self.score += int(dt * 20)

                self.spawn_objects(now)
                self.missiles.update(dt)
                self.rings.update(dt)
                
                for core in self.cores:
                    core.update(dt, self.player)
                self.obstacles.update(dt)

                self.handle_collisions()

                if self.player.lives <= 0 or self.player.energy <= 0:
                    self.game_over = True
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()

            self.screen.fill(COLOR_BG)
            
            for i in range(15):
                sx = (i * 70 - int(self.distance * 2)) % WIDTH
                sy = (i * 37) % (HEIGHT - 60)
                pygame.draw.circle(self.screen, COLOR_WHITE, (sx, sy), 1)

            self.all_sprites.draw(self.screen)
            self.player.draw_extras(self.screen)

            if self.game_over:
                self.hud.draw_game_over(self.screen, self.score, self.distance, self.high_score)
            else:
                self.hud.draw(self.screen, self.player, self.score, self.distance, self.combo, self.high_score, self.get_current_level())

            pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
'''
}

# Create output zip file containing all files packaged under a SkyFlightTest/ folder
zip_filename = "SkyFlightTest.zip"

with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zip_out:
    for filename, content in files.items():
        # Write files locally in current directory
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        # Add to ZIP archive under project folder
        zip_out.writestr(f"SkyFlightTest/{filename}", content)

print(f"✅ Generated all Python source files and created '{zip_filename}' successfully!")