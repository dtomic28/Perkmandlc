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
from powerups.torch import TorchPowerUp


class Train:
    def __init__(self):
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(0, 0)
        self.add_block_flag = False
        self.__speed = 1
        self.active_powerups = []
        self.fog_disabled = False  # Used by fog of war

        # train images
        try:
            image_huntLeft = pygame.image.load("assets/hunt_left.png").convert_alpha()
            self.image_huntLeft = pygame.transform.scale(
                image_huntLeft, (CELL_SIZE, CELL_SIZE)
            )
            image_huntRight = pygame.image.load("assets/hunt_right.png").convert_alpha()
            self.image_huntRight = pygame.transform.scale(
                image_huntRight, (CELL_SIZE, CELL_SIZE)
            )
            image_huntUp = pygame.image.load("assets/hunt_up.png").convert_alpha()
            self.image_huntUp = pygame.transform.scale(
                image_huntUp, (CELL_SIZE, CELL_SIZE)
            )
            image_huntDown = pygame.image.load("assets/hunt_down.png").convert_alpha()
            self.image_huntDown = pygame.transform.scale(
                image_huntDown, (CELL_SIZE, CELL_SIZE)
            )

            image_coalCartHorizontal = pygame.image.load(
                "assets/coal_cart_horizontal.png"
            ).convert_alpha()
            self.image_coalCartHorizontal = pygame.transform.scale(
                image_coalCartHorizontal, (CELL_SIZE, CELL_SIZE)
            )
            image_coalCartVertical = pygame.image.load(
                "assets/coal_cart_vertical.png"
            ).convert_alpha()
            self.image_coalCartVertical = pygame.transform.scale(
                image_coalCartVertical, (CELL_SIZE, CELL_SIZE)
            )
        except Exception:
            print("Error loading train images, using colors instead.")
            self.image_huntLeft = pygame.Surface((CELL_SIZE, CELL_SIZE))
            self.image_huntLeft.fill(TRAIN_HEAD_COLOR)
            self.image_huntRight = pygame.Surface((CELL_SIZE, CELL_SIZE))
            self.image_huntRight.fill(TRAIN_HEAD_COLOR)
            self.image_huntUp = pygame.Surface((CELL_SIZE, CELL_SIZE))
            self.image_huntUp.fill(TRAIN_HEAD_COLOR)
            self.image_huntDown = pygame.Surface((CELL_SIZE, CELL_SIZE))
            self.image_huntDown.fill(TRAIN_HEAD_COLOR)
            self.image_coalCartHorizontal = pygame.Surface((CELL_SIZE, CELL_SIZE))
            self.image_coalCartHorizontal.fill(TRAIN_BODY_COLOR)
            self.image_coalCartVertical = pygame.Surface((CELL_SIZE, CELL_SIZE))
            self.image_coalCartVertical.fill(TRAIN_BODY_COLOR)

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
        elif powerup_type == PowerUpType.TORCH:
            powerup = TorchPowerUp(duration_ms=10000)
        else:
            return  # Unknown or unimplemented powerup type

        powerup.apply(self)
        self.active_powerups.append(powerup)

    def draw(self, screen):
        offset_y = SCREEN_HEIGHT - (CELL_COUNT * CELL_SIZE // 2)
        body = (
            list(reversed(self.body)) if self.direction == Vector2(0, 1) else self.body
        )
        body = self.body

        for index, block in enumerate(body):
            x = int(block.x * CELL_SIZE)
            y = int(block.y * CELL_SIZE // 2 + offset_y)

            if index == 0:
                if self.direction == Vector2(1, 0):  # Moving right
                    screen.blit(self.image_huntRight, (x, y - CELL_SIZE // 2))
                elif self.direction == Vector2(-1, 0):  # Moving left
                    screen.blit(self.image_huntLeft, (x, y - CELL_SIZE // 2))
                elif self.direction == Vector2(0, -1):  # Moving up
                    screen.blit(self.image_huntUp, (x, y - CELL_SIZE // 2))
                elif self.direction == Vector2(0, 1):  # Moving down
                    screen.blit(self.image_huntDown, (x, y - CELL_SIZE // 2))
                continue
            else:
                if self.direction.x != 0:  # Horizontal movement
                    screen.blit(self.image_coalCartHorizontal, (x, y - CELL_SIZE // 2))
                else:  # Vertical movement
                    screen.blit(self.image_coalCartVertical, (x, y - CELL_SIZE // 2))
