from powerups.base_powerup import BasePowerUp


class SpeedBoost(BasePowerUp):
    def __init__(self, duration_ms=5000):
        super().__init__(duration_ms)

    def apply(self, train):
        train.increaseSpeed()

    def revert(self, train):
        train.resetSpeed()
