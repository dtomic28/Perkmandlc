import pygame
from pygame.math import Vector2
from constants import CELL_COUNT, CELL_SIZE, SCREEN_HEIGHT
import random


import pygame
import random
from pygame.math import Vector2
from constants import CELL_COUNT, CELL_SIZE, SCREEN_HEIGHT


class Coal:
    def __init__(self):
        self.positions = []
        self.margin = 3
        try:
            self.image = pygame.image.load("assets/coal.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE // 2))
        except Exception:
            self.image = None

    def clear(self):
        self.positions.clear()

    def spawn_random(self, count=1):
        for _ in range(count):
            x = random.randint(self.margin, CELL_COUNT - 1 - self.margin)
            y = random.randint(0, (CELL_COUNT // 2) - 1) * 2
            y = max(y, self.margin)
            y = min(y, CELL_COUNT - 1 - self.margin)
            self.positions.append(Vector2(x, y))

    def spawn_at(self, pos_list):
        for pos in pos_list:
            self.positions.append(Vector2(pos.x, pos.y))

    def draw(self, screen):
        if not self.image:
            return

        offset_y = SCREEN_HEIGHT - (CELL_COUNT * CELL_SIZE // 2)
        for pos in self.positions:
            x = int(pos.x * CELL_SIZE)
            y = int(pos.y * CELL_SIZE // 2 + offset_y)
            screen.blit(self.image, (x, y))

    def check_pickup(self, head_pos):
        for i, pos in enumerate(self.positions):
            if pos == head_pos:
                del self.positions[i]
                return True
        return False
