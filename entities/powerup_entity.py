from enum import Enum, auto
import pygame
from constants import CELL_COUNT, CELL_SIZE, SCREEN_HEIGHT
from pygame.math import Vector2


class PowerUpType(Enum):
    SPEED_BOOST = (1,)
    TORCH = 2


class PowerUpEntity:
    def __init__(self, type: PowerUpType, pos: Vector2, image):
        self.type = type
        self.pos = pos
        self.image = pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE // 2))

    def draw(self, surface):
        offset_y = SCREEN_HEIGHT - (CELL_COUNT * CELL_SIZE // 2)
        x = int(self.pos.x * CELL_SIZE)
        y = int(self.pos.y * CELL_SIZE // 2 + offset_y)
        surface.blit(self.image, (x, y))
