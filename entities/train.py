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

from entities.powerup_entity import PowerUpType
from powerups.speed_boost import SpeedBoost


class Train:
    def __init__(self):
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(0, 0)
        self.add_block_flag = False
        self.__speed = 1
        self.active_powerups = []

    def __move_once(self):
        if self.direction == Vector2(0, 0):
            return
        new_head = self.body[0] + self.direction
        if self.add_block_flag:
            self.body.insert(0, new_head)
            self.add_block_flag = False
        else:
            self.body = [new_head] + self.body[:-1]

    def __move(self):
        for _ in range(self.__speed):
            self.__move_once()

    def __update_powerups(self):
        # Remove expired powerups after updating them
        self.active_powerups = [p for p in self.active_powerups if p.active]

        # Update each powerup — if it expired, it will mark itself inactive
        for powerup in self.active_powerups:
            powerup.update(self)

    def update(self):
        self.__update_powerups()
        self.__move()

    def grow(self):
        self.add_block_flag = True

    def reset(self):
        self.__init__()

    def increaseSpeed(self):
        self.__speed = 2

    def resetSpeed(self):
        self.__speed = 1

    def collect_powerup(self, powerup_type):
        if powerup_type == PowerUpType.SPEED_BOOST:
            powerup = SpeedBoost(duration_ms=5000)
        else:
            return  # Unknown or unimplemented powerup type

        powerup.apply(self)
        self.active_powerups.append(powerup)

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
