import random
import pygame
import sys
from pygame.math import Vector2
from constants import CELL_COUNT, CELL_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH, SKY_COLOR
from entities.powerup_entity import PowerUpEntity, PowerUpType
from entities.train import Train
from entities.coal import Coal
from entities.ai_train import AITrain
from menu import MainMenu, Menu, YouDiedMenu
from utils import is_first_time, load_difficulty, mark_tutorial_done, save_difficulty

pygame.init()

SCREEN_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SCREEN_UPDATE, 150)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.train = Train()
        self.coal = Coal()
        self.paused = False
        self.pause_menu = None
        self.options_menu = None
        self.you_died_menu = None
        self.main_menu = MainMenu(callback=self.handle_main_menu_selection)
        self.in_main_menu = True
        self.is_multiplayer = False
        self.ai_train = None
        self.difficulty = load_difficulty()
        self.tutorial_mode = is_first_time()
        self.tutorial_step = 0
        self.key_pressed_after_completion = False
        self.world_powerups = []

        self.coal.spawn_random(3)

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
        ]

        if self.is_multiplayer:
            self.tutorial_steps.append(
                {
                    "message": "Great job! You're ready to play. but be careful you are not on your own.",
                    "condition": self.check_key_press_after_completion,
                }
            )
        else:
            self.tutorial_steps.append(
                {
                    "message": "Great job! You're ready to play. but you won't be alone.",
                    "condition": self.check_key_press_after_completion,
                }
            )

    def draw_fog_of_war(self):
        fog_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        fog_surface.fill((0, 0, 0, 245))  # Mostly dark

        if self.difficulty == "Easy":
            return

        radius = {"Easy": 200, "Medium": 120, "Hard": 60}.get(self.difficulty, 120)

        def grid_to_screen(pos: Vector2):
            offset_y = SCREEN_HEIGHT - (CELL_COUNT * CELL_SIZE // 2)
            x = int(pos.x * CELL_SIZE)
            y = int(pos.y * CELL_SIZE // 2 + offset_y - CELL_SIZE // 2)
            return (x + CELL_SIZE // 2, y + CELL_SIZE // 2)  # center of tile

        # Player spotlight
        center = grid_to_screen(self.train.body[0])
        pygame.draw.circle(fog_surface, (0, 0, 0, 0), center, radius)

        # AI spotlight (if multiplayer)
        if self.is_multiplayer and self.ai_train and self.ai_train.alive:
            ai_center = grid_to_screen(self.ai_train.body[0])
            pygame.draw.circle(fog_surface, (0, 0, 0, 0), ai_center, radius)

        self.screen.blit(fog_surface, (0, 0))

    def get_safe_ai_spawn(self):
        safe_margin = 8
        for _ in range(20):
            x = random.randint(safe_margin + 2, CELL_COUNT - safe_margin - 1)
            y = random.randint(safe_margin, CELL_COUNT - safe_margin - 1)
            pos = Vector2(x, y)
            if all(pos.distance_to(p) > safe_margin for p in self.train.body):
                return pos
        return Vector2(CELL_COUNT - 5, CELL_COUNT - 5)  # fallback

    def spawn_random_powerup(self):
        margin = 3
        x = random.randint(margin, CELL_COUNT - 1 - margin)
        y = random.randint(0, (CELL_COUNT // 2) - 1) * 2
        y = max(y, margin)
        y = min(y, CELL_COUNT - 1 - margin)
        pos = Vector2(x, y)
        ptype = random.choice(list(self.powerup_images.keys()))
        image = self.powerup_images[ptype]
        self.world_powerups.append(PowerUpEntity(ptype, pos, image))

    def update(self):
        if self.paused or self.in_main_menu or self.you_died_menu:
            return

        self.train.update()
        self.check_collision()
        self.check_fail()

        if self.is_multiplayer and self.ai_train:
            if self.ai_train.alive:
                avoid = self.train.body
                self.ai_train.update_ai(self.coal.positions, avoid, self.coal)
            elif self.ai_train.ready_to_respawn():
                spawn = self.get_safe_ai_spawn()
                self.ai_train = AITrain(position=spawn)

    def draw_elements(self):
        if self.in_main_menu:
            (self.options_menu or self.main_menu).draw(
                self.screen, SCREEN_WIDTH, SCREEN_HEIGHT
            )
        elif self.you_died_menu:
            self.you_died_menu.draw(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        else:
            self.draw_sky_and_ground()
            self.coal.draw(self.screen)
            self.train.draw(self.screen)
            if self.ai_train and self.ai_train.alive:
                self.ai_train.draw(self.screen)
            for powerup in self.world_powerups:
                powerup.draw(self.screen)
            self.draw_fog_of_war()
            if self.paused:
                (self.options_menu or self.pause_menu).draw(
                    self.screen, SCREEN_WIDTH, SCREEN_HEIGHT
                )
            if self.tutorial_mode and not self.paused:
                self.draw_tutorial_message()
            self.draw_score()

    def check_collision(self):
        # --- Player picks up coal ---
        if self.coal.check_pickup(self.train.body[0]):
            self.train.grow()
            self.coal.spawn_random(2)

        # --- AI picks up coal ---
        if self.ai_train and self.ai_train.alive:
            if self.coal.check_pickup(self.ai_train.body[0]):
                self.ai_train.grow()
                self.coal.spawn_random()

        # --- Remove coal from train body (cleanup) ---
        for block in self.train.body[1:]:
            if block in self.coal.positions:
                self.coal.positions.remove(block)
                self.coal.spawn_random(1)

        # --- Power-up pickup ---
        for pu in self.world_powerups[:]:  # Safe removal while iterating
            if pu.pos == self.train.body[0]:
                self.train.collect_powerup(pu.type)
                self.world_powerups.remove(pu)
                break

        # --- Player ↔ AI collision (Slither.io logic) ---
        if self.ai_train and self.ai_train.alive:
            player_head = self.train.body[0]
            ai_head = self.ai_train.body[0]
            player_body = self.train.body[1:]
            ai_body = self.ai_train.body[1:]

            # AI head hits player body → AI dies
            if ai_head in player_body:
                self.ai_train.die()

            # Player head hits AI body → player dies
            elif player_head in ai_body:
                self.game_over()

            # Head-on collision (optional: both die)
            elif ai_head == player_head:
                print("Head-on collision!")
                self.game_over()
                self.ai_train.die()

    def check_fail(self):
        head = self.train.body[0]
        if head.x < 0 or head.x >= CELL_COUNT or head.y < 0 or head.y >= CELL_COUNT:
            self.game_over()
        if head in self.train.body[1:] and self.train.direction != Vector2(0, 0):
            self.game_over()

    def game_over(self):
        score = len(self.train.body) - 3
        self.you_died_menu = YouDiedMenu(
            callback=self.handle_you_died_menu_selection, current_score=score
        )

    def handle_main_menu_selection(self, option):
        if option == "Start Singleplayer":
            self.in_main_menu = False
            self.ai_train = None
        elif option == "Start Multiplayer":
            self.in_main_menu = False
            self.is_multiplayer = True
            spawn = self.get_safe_ai_spawn()
            if self.ai_train:
                self.ai_train.reset()
            else:
                self.ai_train = AITrain(position=spawn)
        elif option == "Credits":
            self.show_credits()
        elif option == "Options":
            self.show_options_menu()
        elif option == "Quit Game":
            pygame.quit()
            sys.exit()

    def handle_you_died_menu_selection(self, option):
        if option == "Retry":
            self.train.reset()
            self.coal.clear()
            self.coal.spawn_random(3)
            self.world_powerups.clear()
            self.you_died_menu = None

            if self.ai_train:
                self.ai_train.reset()
        elif option == "Main Menu":
            self.return_to_main_menu()

    def return_to_main_menu(self):
        self.__init__()

    def draw_sky_and_ground(self):
        pygame.draw.rect(self.screen, SKY_COLOR, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        offset_y = SCREEN_HEIGHT - (CELL_COUNT * CELL_SIZE // 2)
        for row in range(CELL_COUNT):
            for col in range(CELL_COUNT):
                x = col * CELL_SIZE
                y = row * CELL_SIZE // 2 + offset_y
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE // 2)
                color = (150, 200, 80) if (row + col) % 2 == 0 else (100, 150, 50)
                pygame.draw.rect(self.screen, color, rect)

    def draw_score(self):
        score_text = f"Score: {len(self.train.body) - 3}"
        surface = pygame.font.Font(None, 25).render(score_text, True, (56, 74, 12))
        rect = surface.get_rect(topleft=(SCREEN_WIDTH * 0.05, SCREEN_HEIGHT * 0.05))
        pygame.draw.rect(self.screen, (167, 209, 61), rect.inflate(10, 10))
        self.screen.blit(surface, rect)
        pygame.draw.rect(self.screen, (56, 74, 12), rect.inflate(10, 10), 2)

    def draw_tutorial_message(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        font = pygame.font.Font(None, 36)
        text = font.render(
            self.tutorial_steps[self.tutorial_step]["message"], True, (255, 255, 255)
        )
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.3))
        self.screen.blit(text, rect)

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
                "Pause Menu",
                ["Resume", "Options", "Main Menu", "Quit Game"],
                self.handle_pause_menu_selection,
            )
        else:
            self.pause_menu = None

    def show_options_menu(self):
        self.options_menu = Menu(
            "Options",
            ["Difficulty: " + self.difficulty, "Back"],
            self.handle_options_menu_selection,
        )
        self.pause_menu = None
        self.main_menu = None

    def handle_options_menu_selection(self, option):
        if option.startswith("Difficulty"):
            difficulties = ["Easy", "Medium", "Hard"]
            i = difficulties.index(self.difficulty)
            self.difficulty = difficulties[(i + 1) % len(difficulties)]
            self.options_menu.options[0] = "Difficulty: " + self.difficulty
            save_difficulty(self.difficulty)
        elif option == "Back":
            self.pause_menu = (
                Menu(
                    "Pause Menu",
                    ["Resume", "Options", "Main Menu", "Quit Game"],
                    self.handle_pause_menu_selection,
                )
                if self.paused
                else None
            )
            self.main_menu = MainMenu(callback=self.handle_main_menu_selection)
            self.options_menu = None

    def show_credits(self):
        self.main_menu = Menu(
            "Credits",
            [
                "Tadej Sev\u0161ek",
                "Danijel Tomi\u010d",
                "Tilen Ga\u0161pari\u010d",
                "Back",
            ],
            self.handle_credits_selection,
        )

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
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == SCREEN_UPDATE and not (
            main_game.paused or main_game.in_main_menu or main_game.you_died_menu
        ):
            main_game.update()
        if event.type == pygame.KEYDOWN:
            if not (
                main_game.paused or main_game.in_main_menu or main_game.you_died_menu
            ):
                d = main_game.train.direction
                if event.key == pygame.K_UP and d != Vector2(0, 1):
                    main_game.train.direction = Vector2(0, -1)
                elif event.key == pygame.K_DOWN and d != Vector2(0, -1):
                    main_game.train.direction = Vector2(0, 1)
                elif event.key == pygame.K_LEFT and d != Vector2(1, 0):
                    main_game.train.direction = Vector2(-1, 0)
                elif event.key == pygame.K_RIGHT and d != Vector2(-1, 0):
                    main_game.train.direction = Vector2(1, 0)
                elif event.key == pygame.K_p:
                    main_game.spawn_random_powerup()
            if event.key == pygame.K_ESCAPE:
                main_game.toggle_pause()
            if (
                main_game.tutorial_mode
                and main_game.tutorial_step == len(main_game.tutorial_steps) - 1
            ):
                main_game.key_pressed_after_completion = True

        if main_game.in_main_menu:
            (main_game.options_menu or main_game.main_menu).handle_input(event)
        elif main_game.paused:
            (main_game.pause_menu or main_game.options_menu).handle_input(event)
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
