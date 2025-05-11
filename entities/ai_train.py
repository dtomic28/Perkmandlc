from pygame.math import Vector2
from constants import CELL_COUNT
from entities.train import Train


class AITrain(Train):
    def __init__(self, position=None):
        super().__init__()
        start = position if position else Vector2(15, 10)
        self.body = [start, start - Vector2(1, 0), start - Vector2(2, 0)]
        self.direction = Vector2(1, 0)
        self.alive = True
        self.respawn_timer = 0  # milliseconds timestamp

    def die(self, coal=None):
        if self.respawn_timer == 0:
            print("AI died at:", self.body[0])
            self.alive = False
            if coal:
                coal.spawn_at(self.body)
            import pygame

            self.respawn_timer = pygame.time.get_ticks() + 5000

    def ready_to_respawn(self):
        import pygame

        return (
            not self.alive
            and self.respawn_timer > 0
            and pygame.time.get_ticks() >= self.respawn_timer
        )

    def reset(self, position=None):
        start = position if position else Vector2(15, 10)
        self.body = [start, start - Vector2(1, 0), start - Vector2(2, 0)]
        self.direction = Vector2(1, 0)
        self.alive = True
        self.respawn_timer = 0

    def update_ai(self, coal_positions, avoid_positions, coal=None):
        if not self.alive:
            return

        head_before = self.body[0]
        if coal_positions:
            target = min(coal_positions, key=lambda c: head_before.distance_to(c))
            self.__steer_towards(target, avoid_positions, coal)

        self.update()
        head = self.body[0]

        if not (0 <= head.x < CELL_COUNT and 0 <= head.y < CELL_COUNT):
            print("AI died by wall at:", head)
            self.die(coal)
        elif head in self.body[1:]:
            print("AI died by self-collision at:", head)
            self.die(coal)
        elif head in avoid_positions:
            print("AI died by player collision at:", head)
            self.die(coal)

    def __steer_towards(self, target, avoid_positions, coal):
        import random

        head = self.body[0]
        options = [Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1)]
        opposite = -self.direction
        safe_moves = []

        for option in options:
            new_head = head + option
            future_body = [new_head] + self.body[:-1]

            # Would this move normally be fatal?
            is_collision = (
                new_head in avoid_positions
                or new_head in self.body
                or future_body[0] in future_body[1:]
            )

            # ✅ Allow intentional suicide if we're moving into the player's body
            if is_collision:
                if new_head in avoid_positions and option == self.direction:
                    print(f"AI is intentionally colliding into player at {new_head}")
                    dist = new_head.distance_to(target)
                    safe_moves.append((option, dist))
                    continue
                continue

            # Prefer non-reversing direction
            penalty = 1 if option == opposite else 0
            dist = new_head.distance_to(target) + penalty
            safe_moves.append((option, dist))

        if safe_moves:
            min_dist = min(safe_moves, key=lambda x: x[1])[1]
            candidates = [opt for opt in safe_moves if abs(opt[1] - min_dist) < 0.1]
            self.direction = random.choice(candidates)[0]
        else:
            print(f"AI has no safe move from {head}. Dying.")
            self.die(coal)
