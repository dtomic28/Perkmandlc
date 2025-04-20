import pygame
from abc import ABC, abstractmethod


class BasePowerUp(ABC):
    def __init__(self, duration_ms):
        self.duration = duration_ms
        self.start_time = pygame.time.get_ticks()
        self.active = True

    @abstractmethod
    def apply(self, train):
        pass

    @abstractmethod
    def revert(self, train):
        pass

    def update(self, train):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.revert(train)
            self.active = False
