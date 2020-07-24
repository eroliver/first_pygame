import pygame
import os
import time
import random

# initialize pygame font module
pygame.font.init()
# define the size of the game window
WIDTH, HEIGHT = 750, 750
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooter_Game")

# load images into the game
PLAYER_SHIP = pygame.image.load(os.path.join("assets", "player00.png"))
RED_ENEMY = pygame.image.load(os.path.join("assets", "red_black_enemy.png"))
YELLOW_ENEMY = pygame.image.load(os.path.join("assets", "yellow_black_enemy.png"))
PURPLE_ENEMY = pygame.image.load(os.path.join("assets", "purple_enemy.png"))
PLAYER_BULLET = pygame.image.load(os.path.join("assets", "player_bullet.png"))
ENEMY_BULLET = pygame.image.load(os.path.join("assets", "enemy_bullet.png"))
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "star_background.png")), (WIDTH, HEIGHT))


# define abstract class for ships(players and enemies use)
class Ship:
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SHIP
        self.laser_img = PLAYER_BULLET
        # use pygames mask for pixel perfect collision
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

# the main game loop
def main():
    run = True
    fps = 60
    level = 1
    lives = 5
    main_font = pygame.font.SysFont("Ariel", 50)
    # define player speed
    player_vel = 5

    player = Player(300, 650)

    clock = pygame.time.Clock()

    def redraw_window():
        WINDOW.blit(BG, (0, 0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (0, 255, 150))
        level_label = main_font.render(f"Level: {level}", 1, (0, 255, 150))

        WINDOW.blit(lives_label, (10, 10))
        WINDOW.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        player.draw(WINDOW)

        pygame.display.update()

    while run:
        clock.tick(fps)
        redraw_window()
        # ends the main game loop when the window is closed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x + player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + 50 < HEIGHT:  # down
            player.y += player_vel
        if keys[pygame.K_w] and player.y + player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + 50 < WIDTH:  # right
            player.x += player_vel


main()
