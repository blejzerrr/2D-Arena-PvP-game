import pygame
from game.state_manager import state
from game.states.leaderboard_state import leaderboard_state

class menu_state(state):
    def __init__(self, game):
        state.__init__(self, game)
        self.font_large = pygame.font.Font("assets/images/font.otf", 64)
        self.font_small = pygame.font.Font("assets/images/font.otf", 32)

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    pygame.mixer.music.set_volume(0.2)
                    self.exit_state()
                if event.key == pygame.K_l:
                    lb = leaderboard_state(self.game)
                    lb.enter_state()

    def enter_state(self):
        super().enter_state()
        if not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.load("assets/sounds/lobby.mp3")
                pygame.mixer.music.play(-1)
            except (FileNotFoundError, pygame.error):
                pass  # no music file, run silently
        pygame.mixer.music.set_volume(0.5)

    def render(self, display):
        display.fill((20, 20, 20))
        title = self.font_large.render("Arena PvP", True, (255, 255, 255))
        prompt = self.font_small.render("Press [Enter] or [Space] to Play", True, (200, 200, 200))
        leaderboard = self.font_small.render("Press [L] for Leaderboard", True, (200, 200, 200))
        display.blit(title, title.get_rect(center=(display.get_width() // 2, display.get_height() // 2 - 80)))
        display.blit(prompt, prompt.get_rect(center=(display.get_width() // 2, display.get_height() // 2 + 10)))
        display.blit(leaderboard, leaderboard.get_rect(center=(display.get_width() // 2, display.get_height() // 2 + 60)))