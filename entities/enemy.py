import pygame
import math
import random

from entities.player import BOUNDS_X, BOUNDS_Y 
from game.audio import load_sound

ENEMY_WIDTH = 75
ENEMY_HEIGHT = 75
# ---------------------
# Global particle functions
# ---------------------
particles = []  # global list
huah_sound = None

def get_huah_sound():
    global huah_sound
    if huah_sound is None:
        huah_sound = load_sound("assets/sounds/huah.mp3")
    return huah_sound

def spawn_particles(x, y, width, height):
    """Add a particle to the global particle list"""
    img = pygame.image.load("assets/images/particles.png").convert_alpha()
    img = pygame.transform.scale(img, (width, height))
    particles.append({"img": img, "x": x, "y": y, "alpha": 255})

def update_particles():
    """Fade out all particles"""
    for p in particles[:]:
        p["alpha"] -= 4
        if p["alpha"] <= 0:
            particles.remove(p)
        else:
            # Apply alpha to a copy so per-pixel alpha is preserved
            faded = p["img"].copy()
            faded.set_alpha(p["alpha"])
            p["faded"] = faded

def draw_particles(surface, ox=0, oy=0):
    """Draw all particles"""
    for p in particles:
        img = p.get("faded", p["img"])
        surface.blit(img, (p["x"] + ox, p["y"] + oy))

class Enemy:
    def __init__(self, x, y, width, height, tileset_file, speed, enemy_list):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.health = 3
        self.direction = "down"
        self.frame_index = 0
        self.frame_timer = 0
        self.collider = [width, height] 
        self.max_width = width
        self.max_height = height
        self.collider_width = width
        self.collider_height = height

        tiles = self.load_tileset(tileset_file, 16, 16)
        self.frames = {
            "down": [pygame.transform.scale(tiles[0][i], (width, height)) for i in range(len(tiles[0]))],
            "right": [pygame.transform.scale(tiles[1][i], (width, height)) for i in range(len(tiles[1]))],
            "up": [pygame.transform.scale(tiles[2][i], (width, height)) for i in range(len(tiles[2]))],
            "left": [pygame.transform.flip(pygame.transform.scale(tiles[1][i], (width, height)), True, False) for i in range(len(tiles[1]))]
        }

        enemy_list.append(self)
        self.start_timer = 0

    def cooldown(self):
        if self.start_timer < 1:
            self.start_timer += 0.03
            if self.start_timer > 1:
                self.start_timer = 1

    def get_center(self): 
        return self.x + self.max_width / 2, self.y + self.max_height / 2

    def load_tileset(self, filename, tile_width, tile_height):
        """Loads a tileset image and splits it into a 2D list of subsurfaces"""
        image = pygame.image.load(filename).convert_alpha()
        image_width, image_height = image.get_size()
        tileset = []
        for tile_Y in range(0, image_height // tile_height):
            line = []
            for tile_X in range(0, image_width // tile_width):
                rect = (tile_X * tile_width, tile_Y * tile_height, tile_width, tile_height)
                line.append(image.subsurface(rect))
            tileset.append(line)
        return tileset
    
    def update(self, player):

        self.cooldown()
        if self.start_timer < 1:
            return

        """Move toward the player and animate"""
        # Calculate vector to player
        player_center = (player.rect.centerx, player.rect.centery)
        enemy_center = self.get_center()
        dx = player_center[0] - enemy_center[0]
        dy = player_center[1] - enemy_center[1]
        distance = math.hypot(dx, dy)

        # Normalize and move
        if distance != 0:
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed

        # Determine direction
        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "down" if dy > 0 else "up"

        # Animate
        self.frame_timer += 1
        if self.frame_timer >= 8:  # Adjust speed of animation
            self.frame_index = (self.frame_index + 1) % len(self.frames[self.direction])
            self.frame_timer = 0



    def draw(self, surface, ox=0, oy=0):
        


        frame = self.frames[self.direction][self.frame_index]

        scale = self.start_timer  # 0 → 1

        current_width = int(self.max_width * scale)
        current_height = int(self.max_height * scale)

        if current_width <= 0 or current_height <= 0:
            return

        scaled_frame = pygame.transform.scale(frame, (current_width, current_height))

        # Center the scaled sprite
        draw_x = self.x + (self.max_width - current_width) / 2
        draw_y = self.y + (self.max_height - current_height) / 2

        surface.blit(scaled_frame, (draw_x + ox, draw_y + oy))

    def take_damage(self, damage, enemy_list):
        self.health -= damage
        if self.health <= 0:
            self.destroy(enemy_list)

    def destroy(self, enemy_list, play_sound=True):
        spawn_particles(self.x, self.y, self.max_width, self.max_height)
        if play_sound:
            get_huah_sound().play()
        if self in enemy_list:
            enemy_list.remove(self)
            
def enemy_spawner(player, enemy_list):
    """Generator that spawns an enemy every 60 frames"""
    while True:
        for _ in range(60):  # wait 60 frames
            yield
        # Pick a random spawn position far from the player
        while True:
            randomX = random.randint(BOUNDS_X[0], BOUNDS_X[1] - ENEMY_WIDTH)
            randomY = random.randint(BOUNDS_Y[0], BOUNDS_Y[1] - ENEMY_HEIGHT)
            player_center = player.rect.center  # <-- use this instead of get_center()
            if abs(player_center[0] - randomX) > 250 or abs(player_center[1] - randomY) > 250:
                break
        # Spawn the enemy
        Enemy(randomX, randomY, ENEMY_WIDTH, ENEMY_HEIGHT,
              "assets/images/enemy-Sheet.png", 5, enemy_list)