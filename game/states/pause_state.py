import pygame
from game.state_manager import state

class pause_state(state):
    def __init__(self, game):
        state.__init__(self, game)
        self.font_large = pygame.font.Font("assets/images/font.otf", 64)
        self.font_small = pygame.font.Font("assets/images/font.otf", 32)
        self.overlay = pygame.Surface((game.width, game.height), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 160))

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    pygame.mixer.music.unpause()
                    self.exit_state()

    def enter_state(self):
        super().enter_state()
        pygame.mixer.music.pause()

    def render(self, display):
        display.blit(self.overlay, (0, 0))
        paused = self.font_large.render("Paused", True, (255, 255, 255))
        resume = self.font_small.render("Press [Esc] or [P] to Resume", True, (200, 200, 200))
        display.blit(paused, paused.get_rect(center=(display.get_width() // 2, display.get_height() // 2 - 60)))
        display.blit(resume, resume.get_rect(center=(display.get_width() // 2, display.get_height() // 2 + 20)))