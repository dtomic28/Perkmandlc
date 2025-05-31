import pygame
from powerups.base_powerup import BasePowerUp


class TorchPowerUp(BasePowerUp):
    def apply(self, train):
        train.fog_disabled = True  # 👈 Custom attribute on train

    def revert(self, train):
        train.fog_disabled = False
