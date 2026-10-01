import pygame

PLAYER_WIDTH = 75
PLAYER_HEIGHT = 75

BOUNDS_X = (66, 1214)
BOUNDS_Y = (50, 620)


# ---------- CHARACTER LOADER ----------
def load_tileset(filename, tile_width, tile_height):
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

# ---------- Player ----------
class Player:
    def __init__(self, x, y, width, height, tileset_file, speed):

        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed  
        self.direction = "down" 
        self.frame_index = 0 
        self.frame_timer = 0 
        self.health = self.max_health = 3
        self.collider_width = self.width * 0.1
        self.collider_height = self.height * 0.1
        self.heart_full = pygame.transform.scale(pygame.image.load("assets/images/heart.png").convert_alpha(),(50, 50))
        self.heart_empty = pygame.transform.scale(pygame.image.load("assets/images/heart_empty.png").convert_alpha(),(50, 50))
        self.alive = True

   
        tiles = load_tileset(tileset_file, 16, 16) 

        self.frames = {
            "down": [pygame.transform.scale(tiles[0][i], (width, height)) for i in range(len(tiles[0]))],
            "right": [pygame.transform.scale(tiles[1][i], (width, height)) for i in range(len(tiles[1]))],
            "up": [pygame.transform.scale(tiles[2][i], (width, height)) for i in range(len(tiles[2]))],
            "left": [pygame.transform.flip(pygame.transform.scale(tiles[1][i], (width, height)), True, False) for i in range(len(tiles[1]))]
        }

    def get_center(self): 
        return self.rect.centerx, self.rect.centery

    def update(self, keys, up, down, left, right, game_width, game_height):

        if not self.alive:
            return
        moving = False 

        self.rect.x = max(BOUNDS_X[0], min(self.rect.x, BOUNDS_X[1] - self.width))
        self.rect.y = max(BOUNDS_Y[0], min(self.rect.y, BOUNDS_Y[1] - self.height))

        #up
        if keys[up] and self.rect.top > BOUNDS_Y[0]:
            self.rect.y -= self.speed
            self.direction = "up"
            moving = True
        #down
        elif keys[down] and self.rect.bottom < BOUNDS_Y[1]:
            self.rect.y += self.speed
            self.direction = "down"
            moving = True
        #left
        if keys[left] and self.rect.left > BOUNDS_X[0]:
            self.rect.x -= self.speed
            self.direction = "left"
            moving = True
        #right
        elif keys[right] and self.rect.right < BOUNDS_X[1]:
            self.rect.x += self.speed
            self.direction = "right"
            moving = True

        # Animate only if moving
        if moving:
            self.frame_timer += 1
            if self.frame_timer >= 8:  # controls animation speed
                self.frame_index = (self.frame_index + 1) % len(self.frames[self.direction])
                self.frame_timer = 0
        else:
            self.frame_index = 0  # idle frame

    def display_ui(self, surface):
        for i in range(self.max_health):
            if i < self.health:
                img = self.heart_full
            else:
                img = self.heart_empty
            x = surface.get_width() - (i + 1) * 50 - 10  # from right edge
            y = 10  # still top
            surface.blit(img, (x, y))

    def check_death(self):
        if self.health <= 0:
            self.alive = False

    def draw(self, surface, ox=0, oy=0):
        current_frame = self.frames[self.direction][self.frame_index]
        surface.blit(current_frame, (self.rect.x + ox, self.rect.y +oy))
