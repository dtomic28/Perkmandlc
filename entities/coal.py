import pygame
from pygame.math import Vector2
from constants import CELL_COUNT, CELL_SIZE, SCREEN_HEIGHT
import random


class Coal:
    def __init__(self):
        self.randomize()
        try:
            self.image = pygame.image.load("assets/coal.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE // 2))
        except Exception:
            self.image = None

    def draw(self, screen):
        if not self.image:
            return
        offset_y = SCREEN_HEIGHT - (CELL_COUNT * CELL_SIZE // 2)
        x = int(self.pos.x * CELL_SIZE)
        y = int(self.pos.y * CELL_SIZE // 2 + offset_y)
        screen.blit(self.image, (x, y))

    def randomize(self):
        # Margin from border
        margin = 3

        x = random.randint(margin, CELL_COUNT - 1 - margin)
        y = random.randint(0, (CELL_COUNT // 2) - 1) * 2
        y = max(y, margin)
        y = min(y, CELL_COUNT - 1 - margin)

        self.pos = Vector2(x, y)
