import pygame
from game.state_manager import state

MAX_NAME_LENGTH = 12

class name_entry_state(state):
    def __init__(self, game):
        state.__init__(self, game)
        self.font_large = pygame.font.Font("assets/images/font.otf", 64)
        self.font_medium = pygame.font.Font("assets/images/font.otf", 40)
        self.font_small = pygame.font.Font("assets/images/font.otf", 28)
        self.name = ""

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN and self.name.strip():
                    # Save the name to the game and move to menu
                    self.game.player_name = self.name.strip()
                    self.exit_state()

                elif event.key == pygame.K_BACKSPACE:
                    self.name = self.name[:-1]  # remove last character

                elif len(self.name) < MAX_NAME_LENGTH:
                    # Only allow printable characters
                    if event.unicode.isprintable() and event.unicode != "":
                        self.name += event.unicode

    def render(self, display):
        display.fill((20, 20, 20))

        title = self.font_large.render("Enter Your Name", True, (255, 255, 255))
        display.blit(title, title.get_rect(center=(display.get_width() // 2, display.get_height() // 2 - 120)))

        # Input box
        box_width, box_height = 400, 60
        box_x = display.get_width() // 2 - box_width // 2
        box_y = display.get_height() // 2 - box_height // 2
        pygame.draw.rect(display, (60, 60, 60), (box_x, box_y, box_width, box_height), border_radius=8)
        pygame.draw.rect(display, (255, 255, 255), (box_x, box_y, box_width, box_height), 2, border_radius=8)

        # Name text with blinking cursor
        cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
        name_text = self.font_medium.render(self.name + cursor, True, (255, 255, 255))
        display.blit(name_text, name_text.get_rect(center=(display.get_width() // 2, box_y + box_height // 2)))

        # Hint
        if self.name.strip():
            hint = self.font_small.render("Press [Enter] to confirm", True, (200, 200, 200))
        else:
            hint = self.font_small.render("Type your name to begin", True, (150, 150, 150))
        display.blit(hint, hint.get_rect(center=(display.get_width() // 2, display.get_height() // 2 + 80)))