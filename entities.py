import pygame
import random
import math
from settings import *
from asset_loader import load_image

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT - 60)
        self.layer = random.choice([1, 2, 3])
        self.speed = self.layer * 1.5
        self.size = self.layer

    def update(self, game_speed):
        self.x -= self.speed * game_speed
        if self.x < 0:
            self.x = WIDTH
            self.y = random.randint(0, HEIGHT - 60)

    def draw(self, surface):
        color = (100, 100, 140) if self.layer == 1 else (180, 180, 220) if self.layer == 2 else (255, 255, 255)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


class Particle:
    def __init__(self, x, y, color):
        self.x, self.y, self.color = x, y, color
        self.vx, self.vy = random.uniform(-4, 4), random.uniform(-4, 4)
        self.life = 1.0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 0.03

    def draw(self, surface):
        if self.life > 0:
            s = int(6 * self.life)
            if s > 0:
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), s)


class Ring(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        loaded_img = load_image("ring.png", fallback_size=(36, 36), fallback_color=(255, 215, 0))
        if loaded_img.get_at((0, 0)) == (255, 215, 0):
            self.image = pygame.Surface((36, 36), pygame.SRCALPHA)
            pygame.draw.circle(self.image, COLOR_GOLD, (18, 18), 16, 4)
        else:
            self.image = pygame.transform.scale(loaded_img, (36, 36))
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, speed, player):
        if player.magnet_active:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist < 160 and dist > 0:
                self.rect.x += (dx / dist) * 8.5
                self.rect.y += (dy / dist) * 8.5
        self.rect.x -= speed
        if self.rect.right < -20:
            self.kill()


class EnergyCore(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        loaded_img = load_image("energy_core.png", fallback_size=(32, 32), fallback_color=(0, 255, 0))
        if loaded_img.get_at((0, 0)) == (0, 255, 0):
            self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, COLOR_GREEN, [(14, 0), (28, 14), (14, 28), (0, 14)])
        else:
            self.image = pygame.transform.scale(loaded_img, (32, 32))
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, speed, player):
        self.rect.x -= speed
        if self.rect.right < -20:
            self.kill()

class Obstacle(pygame.sprite.Sprite):
    """Handles Asteroids, Laser Gates, Space Mines, Debris, and Mid-Screen Hazards."""
    def __init__(self, x, y, kind="asteroid"):
        super().__init__()
        self.kind = kind
        self.size = random.randint(35, 60) if kind == "asteroid" else 24

        if kind == "asteroid":
            loaded_img = load_image("asteroid.png", fallback_size=(self.size, self.size), fallback_color=(100, 100, 100))
            if loaded_img.get_at((0, 0)) == (100, 100, 100):
                base_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.circle(base_surf, COLOR_DARK_GRAY, (self.size // 2, self.size // 2), self.size // 2)
                pygame.draw.circle(base_surf, (60, 60, 80), (self.size // 2, self.size // 2), self.size // 2, 3)
                pygame.draw.circle(base_surf, (40, 40, 50), (self.size // 3, self.size // 3), self.size // 6)
                self.original_image = base_surf
            else:
                self.original_image = pygame.transform.scale(loaded_img, (self.size, self.size))

            self.image = self.original_image.copy()
            self.angle = random.randint(0, 360)
            self.rot_speed = random.choice([-1, 1]) * random.uniform(2.0, 4.5)

        elif kind == "laser_gate":
            self.image = pygame.Surface((24, 180), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (255, 30, 30), (8, 0, 8, 180))
            pygame.draw.rect(self.image, (255, 200, 200), (10, 0, 4, 180))
            pygame.draw.rect(self.image, COLOR_DARK_GRAY, (0, 0, 24, 16))
            pygame.draw.rect(self.image, COLOR_DARK_GRAY, (0, 164, 24, 16))

        elif kind == "rotating_laser":
            # Mid-screen rotating double laser
            base_surf = pygame.Surface((140, 140), pygame.SRCALPHA)
            pygame.draw.line(base_surf, COLOR_RED, (10, 70), (130, 70), 6)
            pygame.draw.line(base_surf, COLOR_WHITE, (10, 70), (130, 70), 2)
            pygame.draw.circle(base_surf, COLOR_DARK_GRAY, (70, 70), 14)
            pygame.draw.circle(base_surf, COLOR_CYAN, (70, 70), 6)
            self.original_image = base_surf
            self.image = base_surf.copy()
            self.angle = 0
            self.rot_speed = random.choice([-2.5, 2.5])

        elif kind == "electro_barrier":
            # Horizontal mid-screen electric fence
            self.image = pygame.Surface((90, 20), pygame.SRCALPHA)
            pygame.draw.rect(self.image, COLOR_PURPLE, (0, 6, 90, 8), border_radius=4)
            pygame.draw.circle(self.image, COLOR_CYAN, (0, 10), 10)
            pygame.draw.circle(self.image, COLOR_CYAN, (90, 10), 10)

        elif kind == "mine":
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (220, 20, 20), (16, 16), 12)
            pygame.draw.circle(self.image, COLOR_WHITE, (16, 16), 5)
            for deg in range(0, 360, 45):
                rad = math.radians(deg)
                ex, ey = 16 + math.cos(rad) * 15, 16 + math.sin(rad) * 15
                pygame.draw.line(self.image, COLOR_RED, (16, 16), (ex, ey), 2)
            self.base_y = y
            self.sine_time = random.uniform(0, 6.28)

        elif kind == "debris":
            s = random.randint(16, 24)
            self.image = pygame.Surface((s, s), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (160, 120, 80), (0, 0, s, s), border_radius=3)

        self.rect = self.image.get_rect(center=(x, y))

    def update(self, speed):
        if self.kind == "mine":
            self.sine_time += 0.08
            self.rect.y = self.base_y + int(math.sin(self.sine_time) * 45)
            self.rect.x -= speed * 0.9

        elif self.kind == "debris":
            self.rect.x -= speed * 1.45

        elif self.kind in ["asteroid", "rotating_laser"]:
            self.rect.x -= speed
            self.angle = (self.angle + self.rot_speed) % 360
            rotated_image = pygame.transform.rotate(self.original_image, self.angle)
            center = self.rect.center
            self.image = rotated_image
            self.rect = self.image.get_rect(center=center)

        else:
            self.rect.x -= speed

        if self.rect.right < -80:
            self.kill()


class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y, fast=False):
        super().__init__()
        self.image = pygame.Surface((34, 14), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, COLOR_RED, [(0, 7), (18, 0), (34, 7), (18, 14)])
        pygame.draw.circle(self.image, COLOR_GOLD, (6, 7), 3)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 11.5 if fast else 9.0

    def update(self, player_y):
        if self.rect.centery < player_y:
            self.rect.y += 1.5
        elif self.rect.centery > player_y:
            self.rect.y -= 1.5
        self.rect.x -= self.speed
        if self.rect.right < -40:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, ptype):
        super().__init__()
        self.ptype = ptype
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        color = COLOR_GOLD if ptype == "hyper" else COLOR_PURPLE
        pygame.draw.circle(self.image, color, (15, 15), 14)
        pygame.draw.circle(self.image, COLOR_WHITE, (15, 15), 14, 2)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, speed):
        self.rect.x -= speed
        if self.rect.right < -30:
            self.kill()