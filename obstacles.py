import pygame
import random
from settings import *

class Building(pygame.sprite.Sprite):
    def __init__(self, x, is_big=True):
        super().__init__()
        self.width = random.randint(60, 90) if is_big else random.randint(40, 60)
        self.height = random.randint(220, 320) if is_big else random.randint(120, 180)
        
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_building()
        
        # Ground-anchored building (bottom of screen)
        self.rect = self.image.get_rect(bottomleft=(x, HEIGHT))
        self.speed = 200

    def draw_building(self):
        # Metallic Skyscraper Body
        pygame.draw.rect(self.image, (35, 40, 50), (0, 0, self.width, self.height), border_radius=2)
        pygame.draw.rect(self.image, (70, 80, 100), (0, 0, self.width, self.height), 2, border_radius=2)
        
        # Glowing Yellow Windows Grid
        for wy in range(12, self.height - 15, 20):
            for wx in range(8, self.width - 12, 14):
                if random.random() < 0.8:
                    pygame.draw.rect(self.image, (255, 220, 100), (wx, wy, 8, 12))

    def update(self, dt):
        self.rect.x -= int(self.speed * dt)
        if self.rect.right < -10:
            self.kill()

class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = 28
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Fiery Orbs
        pygame.draw.circle(self.image, (255, 60, 0), (14, 14), 14)
        pygame.draw.circle(self.image, (255, 180, 0), (12, 14), 9)
        pygame.draw.circle(self.image, (255, 255, 200), (10, 14), 4)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = random.randint(320, 480)

    def update(self, dt):
        self.rect.x -= int(self.speed * dt)
        if self.rect.right < -10:
            self.kill()

class EnergyCore(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 255, 150), (12, 12), 10)
        pygame.draw.circle(self.image, (255, 255, 255), (12, 12), 4)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 180

    def update(self, dt):
        self.rect.x -= int(self.speed * dt)
        if self.rect.right < -10:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, p_type):
        super().__init__()
        self.type = p_type
        colors = {"hyper": (255, 215, 0), "magnet": (180, 50, 255), "shield": (0, 220, 255)}
        self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.rect(self.image, colors.get(p_type, (255, 255, 255)), (0, 0, 28, 28), border_radius=6)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 160

    def update(self, dt):
        self.rect.x -= int(self.speed * dt)
        if self.rect.right < -10:
            self.kill()