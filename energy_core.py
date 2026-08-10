import pygame
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
        # Magnet field attraction
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