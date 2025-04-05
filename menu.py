import pygame
from utils import load_high_score, save_high_score


class Menu:
    def __init__(self, title, options, callback):
        self.title = title
        self.options = options
        self.callback = callback
        self.selected_option = 0
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)

    def draw(self, screen, screen_width, screen_height):
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        title_text = self.title_font.render(self.title, True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 3))
        screen.blit(title_text, title_rect)

        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i == self.selected_option else (150, 150, 150)
            option_text = self.font.render(option, True, color)
            option_rect = option_text.get_rect(
                center=(screen_width // 2, screen_height // 2 + i * 50)
            )
            screen.blit(option_text, option_rect)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self.handle_selection()

    def handle_selection(self):
        selected_option = self.options[self.selected_option]
        self.callback(selected_option)


class MainMenu(Menu):
    def __init__(self, callback):
        super().__init__(
            title="Train Game",
            options=["Start Game", "Credits", "Options", "Quit Game"],
            callback=callback,
        )


class OptionsMenu(Menu):
    def __init__(self, callback):
        self.difficulty = "Medium"
        super().__init__(
            title="Options",
            options=["Difficulty: " + self.difficulty, "Back"],
            callback=self.handle_options_menu_selection,
        )
        self.parent_callback = callback

    def handle_options_menu_selection(self, option):
        if option.startswith("Difficulty"):
            difficulties = ["Easy", "Medium", "Hard"]
            current_index = difficulties.index(self.difficulty)
            self.difficulty = difficulties[(current_index + 1) % len(difficulties)]
            self.options[0] = "Difficulty: " + self.difficulty
        elif option == "Back":
            self.parent_callback("Back")


class YouDiedMenu(Menu):
    def __init__(self, callback, current_score):
        self.high_score = load_high_score()
        if current_score > self.high_score:
            self.high_score = current_score
            save_high_score(self.high_score)
        self.current_score = current_score
        super().__init__(
            title="You Died", options=["Retry", "Main Menu"], callback=callback
        )

    def draw(self, screen, screen_width, screen_height):
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render(self.title, True, (255, 255, 255))
        title_rect = title_text.get_rect(
            center=(screen_width // 2, screen_height * 0.3)
        )
        screen.blit(title_text, title_rect)

        text_spacing = screen_height * 0.05

        font = pygame.font.Font(None, 36)
        high_score_text = f"High Score: {self.high_score}"
        high_score_surface = font.render(high_score_text, True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(
            center=(screen_width // 2, screen_height * 0.4)
        )
        screen.blit(high_score_surface, high_score_rect)

        current_score_text = f"Score: {self.current_score}"
        current_score_surface = font.render(current_score_text, True, (255, 255, 255))
        current_score_rect = current_score_surface.get_rect(
            center=(screen_width // 2, screen_height * 0.4 + text_spacing)
        )
        screen.blit(current_score_surface, current_score_rect)

        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i == self.selected_option else (150, 150, 150)
            option_text = font.render(option, True, color)
            option_rect = option_text.get_rect(
                center=(screen_width // 2, screen_height * 0.6 + i * 50)
            )
            screen.blit(option_text, option_rect)


class PauseMenu(Menu):
    def __init__(self, callback):
        options = ["Resume", "Main Menu", "Quit"]
        super().__init__("Paused", options, callback)
