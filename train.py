import pygame
from constants import (
    CELL_COUNT,
    CELL_SIZE,
    SCREEN_HEIGHT,
    TRAIN_BODY_COLOR,
    TRAIN_HEAD_COLOR,
    TRAIN_TAIL_COLOR,
)
from pygame.math import Vector2


class Train:
    def __init__(self):
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(0, 0)
        self.add_block_flag = False

    def move(self):
        if self.direction == Vector2(0, 0):
            return
        new_head = self.body[0] + self.direction
        if self.add_block_flag:
            self.body.insert(0, new_head)
            self.add_block_flag = False
        else:
            self.body = [new_head] + self.body[:-1]

    def grow(self):
        self.add_block_flag = True

    def reset(self):
        self.__init__()

    def draw(self, screen):
        offset_y = SCREEN_HEIGHT - (CELL_COUNT * CELL_SIZE // 2)
        body = (
            list(reversed(self.body)) if self.direction == Vector2(0, 1) else self.body
        )

        for index, block in enumerate(body):
            x = int(block.x * CELL_SIZE)
            y = int(block.y * CELL_SIZE // 2 + offset_y)
            rect = pygame.Rect(x, y - CELL_SIZE // 2, CELL_SIZE, CELL_SIZE)

            if index == 0:
                color = (
                    TRAIN_HEAD_COLOR
                    if self.direction != Vector2(0, 1)
                    else TRAIN_TAIL_COLOR
                )
            elif index == len(body) - 1:
                color = (
                    TRAIN_TAIL_COLOR
                    if self.direction != Vector2(0, 1)
                    else TRAIN_HEAD_COLOR
                )
            else:
                color = TRAIN_BODY_COLOR

            pygame.draw.rect(screen, color, rect)
