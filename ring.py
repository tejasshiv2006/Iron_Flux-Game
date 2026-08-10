import pygame
from settings import *
class Ring(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.radius = 30
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(self.image, COLOR_GOLD, (30, 30), 30, 4)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
    def update(self, dt):
        self.rect.x -= self.speed
        if self.rect.right < 0: self.kill()
