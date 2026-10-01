import pygame

class GameObjects:
    """
    Represents any object in the game world that has a position, size, image, and optional movement.
    Handles collisions using a pygame.Rect.
    """

    def __init__(self, x, y, width, height, image):
        self.width = width
        self.height = height

        # Position & rectangle for collision
        self.rect = pygame.Rect(x, y, width, height)

        # Scale the image to match object size
        self.image = pygame.transform.scale(image, (width, height))

        # Velocity in pixels per frame
        self.velocity = [0, 0]

    def update(self):
        # Move object by velocity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

    def draw(self, surface, ox, oy):
        # Draw the image at the rect's top-left
        surface.blit(self.image, (self.rect.x + ox, self.rect.y + oy))

    def get_center(self):
        # Returns center coordinates
        return self.rect.center