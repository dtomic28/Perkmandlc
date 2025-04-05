import pygame
from pygame.math import Vector2
from constants import CELL_COUNT, CELL_SIZE, SCREEN_HEIGHT
import random


class Coal:
    def __init__(self):
        self.randomize()
        try:
            self.image = pygame.image.load("Graphics/apple.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE // 2))
        except:
            self.image = None

    def draw(self, screen):
        if not self.image:
            return
        offset_y = SCREEN_HEIGHT - (CELL_COUNT * CELL_SIZE // 2)
        x = int(self.pos.x * CELL_SIZE)
        y = int(self.pos.y * CELL_SIZE // 2 + offset_y)
        screen.blit(self.image, (x, y))

    def randomize(self):
        self.pos = Vector2(
            random.randint(0, CELL_COUNT - 1), random.randint(0, CELL_COUNT - 1)
        )
