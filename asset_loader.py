import pygame
import os
from settings import *

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
IMG_DIR = os.path.join(ASSET_DIR, "images")
SOUND_DIR = os.path.join(ASSET_DIR, "sounds")

import os
import pygame

def load_image(filename, fallback_size=(32, 32), fallback_color=(0, 255, 255)):
    path = os.path.join("assets", "images", filename)
    if os.path.exists(path):
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error:
            pass

    # Create fallback transparent surface
    surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
    if fallback_color is not None:
        surf.fill(fallback_color)
    return surf


def load_sound(filename):
    path = os.path.join("assets", "sounds", filename)
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except pygame.error:
            pass
    return None

def load_sound(filename):
    """Loads a sound file safely or returns None if missing."""
    path = os.path.join(SOUND_DIR, filename)
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except pygame.error:
            return None
    return None