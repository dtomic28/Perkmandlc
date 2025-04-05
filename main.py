import sys
import pygame
from pygame.math import Vector2

from constants import (
    CELL_COUNT,
    CELL_SIZE,
    FPS,
    GRASS_COLOR_DARK,
    GRASS_COLOR_LIGHT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SKY_COLOR,
)
from utils import is_first_time, load_high_score, mark_tutorial_done, save_high_score
from train import Train
from coal import Coal
from menu import MainMenu, PauseMenu, YouDiedMenu

SCREEN_UPDATE = pygame.USEREVENT


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Train Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 25)

        self.train = Train()
        self.coal = Coal()

        self.running = True
        self.state = "main_menu"  # can be: main_menu, playing, paused, game_over
        self.tutorial_mode = is_first_time()
        self.tutorial_step = 0
        self.key_after_tutorial = False

        self.main_menu = MainMenu(self.handle_main_menu)
        self.pause_menu = None
        self.game_over_menu = None

        self.high_score = load_high_score()

        pygame.time.set_timer(SCREEN_UPDATE, 150)

    def run(self):
        while self.running:
            self.handle_events()
            if self.state == "playing":
                self.update()
            self.draw()
            pygame.display.update()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            if self.state == "main_menu":
                self.main_menu.handle_input(event)

            elif self.state == "paused" and self.pause_menu:
                self.pause_menu.handle_input(event)

            elif self.state == "game_over" and self.game_over_menu:
                self.game_over_menu.handle_input(event)

            elif self.state == "playing":
                if event.type == SCREEN_UPDATE:
                    self.train.move()
                    self.check_collisions()
                    self.check_fail()

                if event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)

    def handle_key(self, key):
        if key == pygame.K_UP and self.train.direction != Vector2(0, 1):
            self.train.direction = Vector2(0, -1)
        elif key == pygame.K_DOWN and self.train.direction != Vector2(0, -1):
            self.train.direction = Vector2(0, 1)
        elif key == pygame.K_LEFT and self.train.direction != Vector2(1, 0):
            self.train.direction = Vector2(-1, 0)
        elif key == pygame.K_RIGHT and self.train.direction != Vector2(-1, 0):
            self.train.direction = Vector2(1, 0)
        elif key == pygame.K_p:
            self.state = "paused"
            self.pause_menu = PauseMenu(self.handle_pause_menu)
        if self.tutorial_mode and self.tutorial_step == 3:
            self.key_after_tutorial = True

    def handle_main_menu(self, option):
        if option == "Start":
            self.train.reset()
            self.coal.randomize()
            self.tutorial_mode = is_first_time()
            self.tutorial_step = 0
            self.key_after_tutorial = False
        elif option == "Quit":
            self.running = False
            pygame.quit()
            sys.exit()

    def handle_pause_menu(self, option):
        if option == "Resume":
            self.state = "playing"
        elif option == "Main Menu":
            self.state = "main_menu"
        elif option == "Quit":
            self.running = False
            pygame.quit()
            sys.exit()

    def handle_game_over_menu(self, option):
        if option == "Retry":
            self.state = "playing"
            self.train.reset()
            self.coal.randomize()
        elif option == "Main Menu":
            self.state = "main_menu"

    def update(self):
        if self.tutorial_mode:
            self.update_tutorial()

    def update_tutorial(self):
        steps = [
            lambda: self.train.direction != Vector2(0, 0),
            lambda: self.hit_wall(),
            lambda: len(self.train.body) > 3,
            lambda: self.key_after_tutorial,
        ]
        if steps[self.tutorial_step]():
            self.tutorial_step += 1
            if self.tutorial_step >= len(steps):
                self.tutorial_mode = False
                mark_tutorial_done()

    def draw(self):
        self.screen.fill(SKY_COLOR)

        if self.state == "main_menu":
            self.main_menu.draw(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
            return

        if self.state == "paused" and self.pause_menu:
            self.draw_game_scene()
            self.pause_menu.draw(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
            return

        if self.state == "game_over" and self.game_over_menu:
            self.game_over_menu.draw(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
            return

        self.draw_game_scene()

    def draw_game_scene(self):
        self.draw_grass()
        self.coal.draw(self.screen)
        self.train.draw(self.screen)
        self.draw_score()
        if self.tutorial_mode:
            self.draw_tutorial()

    def draw_grass(self):
        offset_y = SCREEN_HEIGHT - (CELL_COUNT * CELL_SIZE // 2)
        for row in range(CELL_COUNT):
            for col in range(CELL_COUNT):
                x = col * CELL_SIZE
                y = row * CELL_SIZE // 2 + offset_y
                color = GRASS_COLOR_LIGHT if (row + col) % 2 == 0 else GRASS_COLOR_DARK
                pygame.draw.rect(
                    self.screen, color, pygame.Rect(x, y, CELL_SIZE, CELL_SIZE // 2)
                )

    def draw_score(self):
        score = len(self.train.body) - 3
        text = self.font.render(f"Score: {score}", True, (56, 74, 12))
        rect = text.get_rect(topleft=(SCREEN_WIDTH * 0.05, SCREEN_HEIGHT * 0.05))
        pygame.draw.rect(self.screen, (167, 209, 61), rect.inflate(10, 10))
        self.screen.blit(text, rect)
        pygame.draw.rect(self.screen, (56, 74, 12), rect.inflate(10, 10), 2)

    def draw_tutorial(self):
        steps = [
            "Welcome to Perkmandelc! Use arrow keys to move.",
            "Don't hit the walls or yourself!",
            "Collect coal to grow your train!",
            "You're ready! Press any key to start.",
        ]
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        msg = self.font.render(steps[self.tutorial_step], True, (255, 255, 255))
        rect = msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.3))
        self.screen.blit(msg, rect)

    def check_collisions(self):
        if self.train.body[0] == self.coal.pos:
            self.train.grow()
            self.coal.randomize()
        while self.coal.pos in self.train.body:
            self.coal.randomize()

    def check_fail(self):
        if self.hit_wall() or self.hit_self():
            current_score = len(self.train.body) - 3
            if current_score > self.high_score:
                self.high_score = current_score
                save_high_score(current_score)
            self.state = "game_over"
            self.game_over_menu = YouDiedMenu(
                self.handle_game_over_menu, current_score, self.high_score
            )

    def hit_wall(self):
        head = self.train.body[0]
        return not (0 <= head.x < CELL_COUNT and 0 <= head.y < CELL_COUNT)

    def hit_self(self):
        head = self.train.body[0]
        return head in self.train.body[1:] and self.train.direction != Vector2(0, 0)


if __name__ == "__main__":
    Game().run()
