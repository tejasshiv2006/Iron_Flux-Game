import pygame
import random
from settings import *

class Star:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.speed = random.uniform(40, 200)
        self.size = random.randint(1, 3)

    def update(self, dt, boosting=False):
        speed_mult = 2.5 if boosting else 1.0
        self.x -= self.speed * speed_mult * dt
        if self.x < 0:
            self.x = self.width
            self.y = random.randint(0, self.height)

    def draw(self, surface):
        color = (200, 220, 255) if self.size > 1 else (100, 120, 160)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-120, 120)
        self.vy = random.uniform(-120, 120)
        self.lifetime = random.uniform(0.3, 0.7)
        self.radius = random.randint(2, 5)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        return self.lifetime > 0

    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class ScorePopup:
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text
        self.lifetime = 1.0

    def update(self, dt):
        self.y -= 30 * dt
        self.lifetime -= dt
        return self.lifetime > 0

    def draw(self, surface, font):
        if self.lifetime > 0:
            txt_surf = font.render(self.text, True, COLOR_GOLD)
            surface.blit(txt_surf, (self.x - txt_surf.get_width() // 2, self.y))