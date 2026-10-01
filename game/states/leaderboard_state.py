import pygame
from game.state_manager import state
from game.highscores import get_top_scores

class leaderboard_state(state):
    def __init__(self, game):
        state.__init__(self, game)
        self.font_large = pygame.font.Font("assets/images/font.otf", 56)
        self.font_medium = pygame.font.Font("assets/images/font.otf", 32)
        self.font_small = pygame.font.Font("assets/images/font.otf", 26)
        self.scores = []

    def enter_state(self):
        super().enter_state()
        self.scores = get_top_scores(10)  # fetch fresh scores every time it opens

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    self.exit_state()  # return to menu

    def render(self, display):
        display.fill((20, 20, 20))

        title = self.font_large.render("Leaderboard", True, (255, 255, 255))
        display.blit(title, title.get_rect(center=(display.get_width() // 2, 80)))

        if not self.scores:
            empty = self.font_medium.render("No scores yet!", True, (150, 150, 150))
            display.blit(empty, empty.get_rect(center=(display.get_width() // 2, display.get_height() // 2)))
        else:
            # Column headers
            headers = self.font_small.render("#       Name                Score", True, (180, 180, 180))
            display.blit(headers, headers.get_rect(center=(display.get_width() // 2, 150)))
            pygame.draw.line(display, (80, 80, 80),
                             (display.get_width() // 2 - 300, 170),
                             (display.get_width() // 2 + 300, 170), 1)

            for i, (name, score) in enumerate(self.scores):
                # Highlight top 3
                if i == 0:
                    colour = (255, 215, 0)   # gold
                elif i == 1:
                    colour = (192, 192, 192) # silver
                elif i == 2:
                    colour = (205, 127, 50)  # bronze
                else:
                    colour = (255, 255, 255)

                row = self.font_medium.render(f"{i + 1:<4}  {name:<16}  {score}", True, colour)
                y = 190 + i * 42
                display.blit(row, row.get_rect(center=(display.get_width() // 2, y)))

        back = self.font_small.render("Press [Esc] to go back", True, (150, 150, 150))
        display.blit(back, back.get_rect(center=(display.get_width() // 2, display.get_height() - 40)))