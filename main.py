import random
import pygame
import sys
from pygame.math import Vector2
from constants import CELL_COUNT, CELL_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH, SKY_COLOR
from entities.powerup_entity import PowerUpEntity, PowerUpType
from entities.train import Train
from entities.coal import Coal
from menu import MainMenu, Menu, YouDiedMenu
from utils import is_first_time, mark_tutorial_done

pygame.init()

SCREEN_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SCREEN_UPDATE, 150)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.game_font = pygame.font.Font(None, 25)
        self.train = Train()
        self.coal = Coal()
        self.paused = False
        self.pause_menu = None
        self.options_menu = None
        self.you_died_menu = None
        self.main_menu = MainMenu(callback=self.handle_main_menu_selection)
        self.in_main_menu = True
        self.difficulty = "Medium"
        self.tutorial_mode = is_first_time()
        self.tutorial_step = 0
        self.key_pressed_after_completion = False
        self.world_powerups = []
        self.powerup_images = {
            PowerUpType.SPEED_BOOST: pygame.image.load(
                "assets/speed_boost_temp.png"
            ).convert_alpha(),
        }
        self.tutorial_steps = [
            {
                "message": "Welcome to Perkmandelc! Use the arrow keys to move.",
                "condition": self.check_movement,
            },
            {
                "message": "Be careful! Don't hit the walls or yourself. (Please try to kill yourself...to progress in the tutorial)",
                "condition": self.check_wall_collision,
            },
            {
                "message": "You did it! Now Collect coals to get more carts and score points.",
                "condition": self.check_apple_eaten,
            },
            {
                "message": "Great job! You're ready to play on your own.",
                "condition": self.check_key_press_after_completion,
            },
        ]

    def spawn_random_powerup(self):
        margin = 3  # avoid edge
        x = random.randint(margin, CELL_COUNT - 1 - margin)
        y = random.randint(0, (CELL_COUNT // 2) - 1) * 2
        y = max(y, margin)
        y = min(y, CELL_COUNT - 1 - margin)

        pos = Vector2(x, y)
        ptype = random.choice(list(self.powerup_images.keys()))
        image = self.powerup_images[ptype]

        self.world_powerups.append(PowerUpEntity(ptype, pos, image))

    def update(self):
        if not self.paused and not self.in_main_menu and not self.you_died_menu:
            self.train.update()
            self.check_collision()
            self.check_fail()

    def draw_tutorial_message(self):
        if self.tutorial_mode and self.tutorial_step < len(self.tutorial_steps):
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))

            font = pygame.font.Font(None, 36)
            text = font.render(
                self.tutorial_steps[self.tutorial_step]["message"],
                True,
                (255, 255, 255),
            )

            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.3))
            self.screen.blit(text, text_rect)

    def draw_elements(self):
        if self.in_main_menu:
            if self.options_menu:
                self.options_menu.draw(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
            else:
                self.main_menu.draw(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        elif self.you_died_menu:
            self.you_died_menu.draw(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        else:
            self.draw_sky_and_ground()
            self.coal.draw(self.screen)
            self.train.draw(self.screen)
            self.draw_score()
            for powerup in self.world_powerups:
                powerup.draw(self.screen)
            if self.paused:
                if self.options_menu:
                    self.options_menu.draw(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
                elif self.pause_menu:
                    self.pause_menu.draw(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
            if self.tutorial_mode and not self.paused:
                self.draw_tutorial_message()

    def check_movement(self):
        return self.train.direction != Vector2(0, 0)

    def check_wall_collision(self):
        head = self.train.body[0]
        return (
            head.x == 0
            or head.x == CELL_COUNT - 1
            or head.y == 0
            or head.y == CELL_COUNT - 1
        )

    def check_apple_eaten(self):
        return len(self.train.body) > 3

    def check_key_press_after_completion(self):
        self.train.direction = Vector2(0, 0)
        return self.key_pressed_after_completion

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_menu = Menu(
                title="Pause Menu",
                options=["Resume", "Options", "Main Menu", "Quit Game"],
                callback=self.handle_pause_menu_selection,
            )
        else:
            self.pause_menu = None

    def handle_main_menu_selection(self, option):
        if option == "Start Game":
            self.in_main_menu = False
        elif option == "Credits":
            self.show_credits()
        elif option == "Options":
            self.show_options_menu()
        elif option == "Quit Game":
            pygame.quit()
            sys.exit()

    def show_options_menu(self):
        self.options_menu = Menu(
            title="Options",
            options=["Difficulty: " + self.difficulty, "Back"],
            callback=self.handle_options_menu_selection,
        )
        self.pause_menu = None
        self.main_menu = None

    def handle_options_menu_selection(self, option):
        if option.startswith("Difficulty"):
            difficulties = ["Easy", "Medium", "Hard"]
            current_index = difficulties.index(self.difficulty)
            self.difficulty = difficulties[(current_index + 1) % len(difficulties)]
            self.options_menu.options[0] = "Difficulty: " + self.difficulty
        elif option == "Back":
            if self.paused:
                self.pause_menu = Menu(
                    title="Pause Menu",
                    options=["Resume", "Options", "Main Menu", "Quit Game"],
                    callback=self.handle_pause_menu_selection,
                )
            else:
                self.main_menu = MainMenu(callback=self.handle_main_menu_selection)
            self.options_menu = None

    def show_credits(self):
        credits_menu = Menu(
            title="Credits",
            options=["Tadej Sevšek", "Danijel Tomič", "Tilen Gašparič", "Back"],
            callback=self.handle_credits_selection,
        )
        self.main_menu = credits_menu

    def handle_credits_selection(self, option):
        if option == "Back":
            self.main_menu = MainMenu(callback=self.handle_main_menu_selection)

    def handle_pause_menu_selection(self, option):
        if option == "Resume":
            self.paused = False
        elif option == "Options":
            self.show_options_menu()
        elif option == "Main Menu":
            self.return_to_main_menu()
        elif option == "Quit Game":
            pygame.quit()
            sys.exit()

    def return_to_main_menu(self):
        self.in_main_menu = True
        self.paused = False
        self.pause_menu = None
        self.options_menu = None
        self.you_died_menu = None
        self.main_menu = MainMenu(callback=self.handle_main_menu_selection)
        self.train.reset()

    def check_collision(self):
        if self.coal.pos == self.train.body[0]:
            self.coal.randomize()
            self.train.grow()
        for block in self.train.body[1:]:
            if block == self.coal.pos:
                self.coal.randomize()
        for pu in self.world_powerups:
            if pu.pos == self.train.body[0]:  # Train head
                self.train.collect_powerup(pu.type)
                self.world_powerups.remove(pu)
                break

    def check_fail(self):
        if (
            not 0 <= self.train.body[0].x < CELL_COUNT
            or not 0 <= self.train.body[0].y < CELL_COUNT
        ):
            self.game_over()
        for block in self.train.body[1:]:
            if block == self.train.body[0] and self.train.direction != Vector2(0, 0):
                self.game_over()

    def game_over(self):
        current_score = len(self.train.body) - 3
        self.you_died_menu = YouDiedMenu(
            callback=self.handle_you_died_menu_selection, current_score=current_score
        )

    def handle_you_died_menu_selection(self, option):
        if option == "Retry":
            self.train.reset()
            self.coal.randomize()
            self.you_died_menu = None
        elif option == "Main Menu":
            self.return_to_main_menu()

    def draw_sky_and_ground(self):
        pygame.draw.rect(self.screen, SKY_COLOR, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        visual_offset_y = SCREEN_HEIGHT - (CELL_COUNT * CELL_SIZE // 2)

        for row in range(CELL_COUNT):
            for col in range(CELL_COUNT):
                x_pos = col * CELL_SIZE
                y_pos = row * CELL_SIZE // 2 + visual_offset_y

                top_left = (x_pos, y_pos)
                top_right = (x_pos + CELL_SIZE, y_pos)
                bottom_left = (x_pos, y_pos + CELL_SIZE // 2)
                bottom_right = (x_pos + CELL_SIZE, y_pos + CELL_SIZE // 2)

                if (row + col) % 2 == 0:
                    pygame.draw.polygon(
                        self.screen,
                        (150, 200, 80),
                        [top_left, top_right, bottom_right, bottom_left],
                    )  # Light green
                else:
                    pygame.draw.polygon(
                        self.screen,
                        (100, 150, 50),
                        [top_left, top_right, bottom_right, bottom_left],
                    )  # Dark green

    def draw_score(self):
        score_text = "Score: " + str(len(self.train.body) - 3)
        score_surface = pygame.font.Font(None, 25).render(
            score_text, True, (56, 74, 12)
        )

        score_x = int(SCREEN_WIDTH * 0.05)
        score_y = int(SCREEN_HEIGHT * 0.05)

        score_rect = score_surface.get_rect(topleft=(score_x, score_y))

        pygame.draw.rect(self.screen, (167, 209, 61), score_rect.inflate(10, 10))

        self.screen.blit(score_surface, score_rect)

        pygame.draw.rect(self.screen, (56, 74, 12), score_rect.inflate(10, 10), 2)


pygame.time.set_timer(SCREEN_UPDATE, 150)
main_game = Game()

while True:
    if main_game.tutorial_mode:
        current_step = main_game.tutorial_steps[main_game.tutorial_step]
        if current_step["condition"]():
            main_game.tutorial_step += 1
            if main_game.tutorial_step >= len(main_game.tutorial_steps):
                main_game.tutorial_mode = False
                mark_tutorial_done()
            else:
                main_game.key_pressed_after_completion = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if (
            event.type == SCREEN_UPDATE
            and not main_game.paused
            and not main_game.in_main_menu
            and not main_game.you_died_menu
        ):
            main_game.update()
        if event.type == pygame.KEYDOWN:
            if (
                not main_game.paused
                and not main_game.in_main_menu
                and not main_game.you_died_menu
            ):
                if event.key == pygame.K_UP and main_game.train.direction != Vector2(
                    0, 1
                ):
                    main_game.train.direction = Vector2(0, -1)
                if event.key == pygame.K_DOWN and main_game.train.direction != Vector2(
                    0, -1
                ):
                    main_game.train.direction = Vector2(0, 1)
                if event.key == pygame.K_LEFT and main_game.train.direction != Vector2(
                    1, 0
                ):
                    main_game.train.direction = Vector2(-1, 0)
                if event.key == pygame.K_RIGHT and main_game.train.direction != Vector2(
                    -1, 0
                ):
                    main_game.train.direction = Vector2(1, 0)

                if event.key == pygame.K_p:
                    main_game.spawn_random_powerup()

            if event.key == pygame.K_ESCAPE:
                main_game.toggle_pause()
            if (
                main_game.tutorial_mode
                and main_game.tutorial_step == len(main_game.tutorial_steps) - 1
            ):
                main_game.key_pressed_after_completion = True
        if main_game.in_main_menu:
            if main_game.options_menu:
                main_game.options_menu.handle_input(event)
            else:
                main_game.main_menu.handle_input(event)
        elif main_game.paused:
            if main_game.pause_menu:
                main_game.pause_menu.handle_input(event)
            elif main_game.options_menu:
                main_game.options_menu.handle_input(event)
        elif main_game.you_died_menu:
            main_game.you_died_menu.handle_input(event)

    main_game.screen.fill(SKY_COLOR)
    if main_game.in_main_menu:
        main_game.screen.fill((0, 0, 0))
    elif main_game.you_died_menu:
        main_game.screen.fill((255, 0, 0))
    main_game.draw_elements()
    pygame.display.update()

    main_game.clock.tick(60)
