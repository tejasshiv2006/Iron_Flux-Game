import pygame, math
from settings import *
class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y, target):
        super().__init__()
        self.image = pygame.Surface((20, 8), pygame.SRCALPHA)
        pygame.draw.rect(self.image, COLOR_RED, (0, 0, 20, 8), border_radius=3)
        pygame.draw.polygon(self.image, COLOR_GOLD, [(-4, 2), (0, 4), (-4, 6)])
        self.rect = self.image.get_rect(center=(x, y))
        self.target, self.speed = target, 7
        self.tracking_time = pygame.time.get_ticks() + 2000
    def update(self, dt):
        if pygame.time.get_ticks() < self.tracking_time and self.target:
            dx, dy = self.target.rect.centerx - self.rect.centerx, self.target.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist != 0: self.rect.x += (dx / dist) * self.speed; self.rect.y += (dy / dist) * self.speed
        else: self.rect.x -= self.speed * 1.2
        if self.rect.right < 0 or self.rect.top > HEIGHT or self.rect.bottom < 0: self.kill()
