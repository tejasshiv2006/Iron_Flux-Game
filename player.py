import pygame
import random
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        self.width = 44
        self.height = 40
        
        # High base speed for all modes
        self.speed = 1100
        
        # Ignite Mode State
        self.is_ignited = False
        self.ignite_timer = 0
        
        self.image = pygame.Surface((self.width + 12, self.height + 12), pygame.SRCALPHA)
        self.draw_ironman()
        
        self.rect = self.image.get_rect(center=(x, y))

    def activate_ignite(self, duration=5.0):
        self.is_ignited = True
        self.ignite_timer = duration

    def draw_ironman(self):
        self.image.fill((0, 0, 0, 0))
        offset_x, offset_y = 6, 6

        # Ignite Mode Visual Effects (Aura/Shield)
        if self.is_ignited:
            # Fiery Shield / Speed Aura
            pygame.draw.ellipse(self.image, (255, 120, 0, 100), (0, 0, self.width + 12, self.height + 12))
            # Mega Repulsor Flames
            pygame.draw.circle(self.image, (255, 200, 0), (offset_x - 4, offset_y + 28), 9)
            pygame.draw.circle(self.image, (255, 255, 255), (offset_x - 4, offset_y + 28), 4)
        else:
            # Standard Repulsor Flames
            pygame.draw.circle(self.image, (0, 220, 255), (offset_x + 4, offset_y + 28), 5)
            pygame.draw.circle(self.image, (255, 255, 255), (offset_x + 4, offset_y + 28), 2)

        # Red Armor Torso & Helmet
        pygame.draw.rect(self.image, (180, 20, 30), (offset_x + 12, offset_y + 10, 22, 22), border_radius=5)
        pygame.draw.ellipse(self.image, (190, 25, 35), (offset_x + 24, offset_y + 4, 16, 16))

        # Gold Faceplate & Shoulders
        pygame.draw.rect(self.image, (240, 190, 40), (offset_x + 32, offset_y + 8, 7, 8), border_radius=2)
        pygame.draw.rect(self.image, (230, 180, 30), (offset_x + 16, offset_y + 6, 8, 6), border_radius=2)

        # Chest Arc Reactor (Glows Gold during Ignite Mode)
        reactor_color = (255, 215, 0) if self.is_ignited else (0, 240, 255)
        pygame.draw.circle(self.image, reactor_color, (offset_x + 22, offset_y + 21), 4)
        pygame.draw.circle(self.image, (255, 255, 255), (offset_x + 22, offset_y + 21), 2)

    def update(self, dt, target_y=None, hand_active=False):
        # Update Ignite Mode Duration
        if self.is_ignited:
            self.ignite_timer -= dt
            if self.ignite_timer <= 0:
                self.is_ignited = False
                self.ignite_timer = 0

        self.draw_ironman()

        # Same movement speed regardless of Ignite status
        current_speed = self.speed

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= current_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += current_speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= current_speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += current_speed * dt

        self.rect.x += int(dx)
        self.rect.y += int(dy)

        # Responsive gesture tracking
        if hand_active and target_y is not None:
            self.rect.centery += int((target_y - self.rect.centery) * 0.70)

        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))