import pygame, time, random
from entities.player import Player, PLAYER_HEIGHT, PLAYER_WIDTH, BOUNDS_X, BOUNDS_Y
from entities.GameObjects import GameObjects
from entities.projectile import shoot, check_collisions
from entities.enemy import Enemy, enemy_spawner, update_particles, draw_particles, ENEMY_WIDTH, ENEMY_HEIGHT, particles
from game.state_manager import state
from game.states.menu_state import menu_state
from game.states.pause_state import pause_state
from game.states.name_entry_state import name_entry_state
from game.highscores import init_db, save_score
from game.audio import load_sound

pygame.init()
pygame.mixer.init()
pygame.font.get_init()
 
TEXT_FONT = pygame.font.Font("assets/images/font.otf", 32)
 
# Game constants
WIDTH, HEIGHT = 1280, 720
shoot_cooldown = 300  # ms between shots
FRAME_RATE = 120
ANIMATION_FRAME_RATE = 10
#screen shake
def screen_shake(intensity, amplitude):
    s = -1
    for _ in range(3):
        for x in range(0, amplitude, intensity):
            yield (x * s, 0)
        for x in range(amplitude, 0, -intensity):
            yield (x * s, 0)
        s *= -1
 
 
class Game:
    def __init__(self):
        pygame.init()
        self.state = "playing"
        self.width = WIDTH
        self.height = HEIGHT
        self.shake_gen = None
        self.shake_offset = (0, 0)
        self.cursor_scale = 1
        self.score = 0
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Arena PvP")
        
        # Timing
        self.clock = pygame.time.Clock()
        self.last_shot_time = 0
 
        # Players
        self.player1 = Player(WIDTH // 2 - PLAYER_WIDTH // 2,HEIGHT // 2 - PLAYER_HEIGHT // 2,PLAYER_WIDTH,PLAYER_HEIGHT,"assets/images/player-model.png",5)
       ## self.player2 = Player(10, self.height - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT, "assets/images/player-model.png", 5) ##
 
        #enemies
        self.enemies = []
        self.enemy_gen = enemy_spawner(self.player1, self.enemies)
 
        # Bullets
        self.bullets = []
 
        # Background
        self.bg = pygame.image.load("assets/images/background.png")
        self.bg = pygame.transform.smoothscale(self.bg, (self.width, self.height))
 
        # Cursor
        self.cursor_img = pygame.image.load("assets/images/cursor.png").convert_alpha()
        self.cursor_img = pygame.transform.scale(self.cursor_img, (self.cursor_img.get_width()*2, self.cursor_img.get_height()*2))
        self.cursor_rect = self.cursor_img.get_rect()
        pygame.mouse.set_visible(False)
 
        self.game_over = False
        self.running = True
        self.player_name = "Player"  # default, overwritten by name entry

        # Sound effects
        self.death_sound = load_sound("assets/sounds/death.mp3")
        self.eek_sound = load_sound("assets/sounds/eek.mp3")

        # Initialise database
        init_db()

        # State stack — name entry first, then menu underneath
        self.state_stack = []
        menu = menu_state(self)
        menu.enter_state()
        name_entry = name_entry_state(self)
        name_entry.enter_state()  # pushed on top, so shows first
        
 
    def handle_events(self):
        events = pygame.event.get()
        stack_before = len(self.state_stack)
 
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
 
            if event.type == pygame.KEYDOWN:
                # Restart from game over
                if self.game_over and event.key == pygame.K_r:
                    self.restart_game()
 
                # Return to main menu from game over
                if self.game_over and event.key == pygame.K_m:
                    self.restart_game()
                    menu = menu_state(self)
                    menu.enter_state()
 
                # Toggle pause (only when actually playing)
                if not self.game_over and len(self.state_stack) == 0:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        pause = pause_state(self)
                        pause.enter_state()
 
        # Only pass events to active state if it was already there before this frame
        if self.state_stack and len(self.state_stack) == stack_before:
            self.state_stack[-1].update(events)
 
    def display_score(self):
        score_text = TEXT_FONT.render(f'Score: {self.score}', True, (0, 0, 0))
        self.screen.blit(score_text, (score_text.get_width() // 2, 25))
 
    def restart_game(self):
        # Reset player
        self.player1.health = self.player1.max_health
        self.player1.rect.x = self.width // 2 - PLAYER_WIDTH // 2
        self.player1.rect.y = self.height // 2 - PLAYER_HEIGHT // 2
        self.player1.alive = True
 
        # Clear enemies and bullets
        self.enemies.clear()
        self.bullets.clear()
        particles.clear()
        self.death_sound.stop()
        pygame.mixer.music.set_volume(0.1)

        # Reset game over flag
        pygame.mouse.set_visible(False)
        self.game_over = False
        self.score = 0
   

 
    def update(self):
        """Update game objects each frame"""
 
        if self.state_stack or self.game_over:
            return


        #player and enemy movement
        keys = pygame.key.get_pressed()
        self.player1.update(keys, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, self.width, self.height)
        ##self.player2.update(keys, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, self.width, self.height)##
 
        if self.player1.alive:
            for enemy in self.enemies[:]:
                enemy.update(self.player1)
            next(self.enemy_gen)
            
        # Shooting
        mouse_pressed = pygame.mouse.get_pressed()
        current_time = pygame.time.get_ticks()
        if mouse_pressed[0] and (current_time - self.last_shot_time >= shoot_cooldown):
            shoot(self.player1, pygame.mouse.get_pos(), self.bullets)
            self.last_shot_time = current_time
            self.cursor_scale = 1.4
 
 
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
 
            bullet_center = bullet.get_center()
            if not (BOUNDS_X[0] < bullet_center[0] < BOUNDS_X[1] and
                    BOUNDS_Y[0] < bullet_center[1] < BOUNDS_Y[1]):
 
                self.bullets.remove(bullet)
        
 
        for e in self.enemies[:]:
            if check_collisions(self.player1, e):
                self.player1.health -= 1
                self.player1.health = max(0, self.player1.health)
                self.eek_sound.play()
                self.player1.check_death()
                e.destroy(self.enemies, play_sound=False)
                continue
            for b in self.bullets[:]:
                if check_collisions(e, b):
                    e.take_damage(1, self.enemies)
                    if b in self.bullets:
                        self.bullets.remove(b)
                    if e.health <= 0:
                        self.score += 1
 
                    if e.health <=0:
                        self.shake_gen = screen_shake(5,20)
 
        if self.shake_gen:
            try:
                self.shake_offset = next(self.shake_gen)
            except StopIteration:
                self.shake_gen = None
                self.shake_offset = (0, 0)
 
        self.player1.check_death()
        if not self.player1.alive:
            self.game_over = True
            save_score(self.player_name, self.score)
            self.death_sound.play()
            pygame.mixer.music.set_volume(0)
 
        update_particles()
 
 
        if self.cursor_scale > 1:
            self.cursor_scale -= 0.04
            if self.cursor_scale < 1:
                self.cursor_scale = 1
 
        # Update cursor
 
        self.cursor_rect.center = pygame.mouse.get_pos()
 
    def draw(self):
        if not self.game_over:
            # Normal game rendering
            ox, oy = self.shake_offset
            self.screen.blit(self.bg, (ox, oy))
            draw_particles(self.screen, ox, oy)
 
            for enemy in self.enemies:
                enemy.draw(self.screen, ox, oy)
 
            for bullet in self.bullets:
                bullet.draw(self.screen, ox, oy)
            self.player1.draw(self.screen, ox, oy)
 
            self.player1.display_ui(self.screen)
            self.display_score()
 
            scaled_cursor = pygame.transform.scale(self.cursor_img, (int(self.cursor_img.get_width() * self.cursor_scale), int(self.cursor_img.get_height() * self.cursor_scale)))
            rect = scaled_cursor.get_rect(center=pygame.mouse.get_pos())
            self.screen.blit(scaled_cursor, rect)
 
            # Render active state (pause) on top if present
            if self.state_stack:
                self.state_stack[-1].render(self.screen)
 
        else:
            self.screen.fill((20, 20, 20))
            pygame.mouse.set_visible(True)
 
            game_over_text = TEXT_FONT.render("Game Over!", True, (255, 255, 255))
            score_text = TEXT_FONT.render(f"Score: {self.score}", True, (255, 255, 255))
            restart_text = TEXT_FONT.render("Press [R] to Restart", True, (255, 255, 255))
            menu_text = TEXT_FONT.render("Press [M] for Main Menu", True, (255, 255, 255))
 
            self.screen.blit(game_over_text, game_over_text.get_rect(center=(self.width // 2, self.height // 2 - 80)))
            self.screen.blit(score_text, score_text.get_rect(center=(self.width // 2, self.height // 2 - 20)))
            self.screen.blit(restart_text, restart_text.get_rect(center=(self.width // 2, self.height // 2 + 40)))
            self.screen.blit(menu_text, menu_text.get_rect(center=(self.width // 2, self.height // 2 + 100)))
 
        pygame.display.update()
 
 
    def run(self):
        """Main game loop"""
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()
 
        pygame.quit()