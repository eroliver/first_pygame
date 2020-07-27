import pygame
import os
import time
import random
import math

# TODO turn ships into dragons
# initialize pygame font module
pygame.font.init()
# define the size of the game window
WIDTH, HEIGHT = 750, 750
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dragon_Shooter_Game")

# load images into the game
PLAYER_DRAGON = pygame.image.load(os.path.join("assets", "player_dragon_blue.png"))
RED_ENEMY = pygame.image.load(os.path.join("assets", "red_dragon.png"))
YELLOW_ENEMY = pygame.image.load(os.path.join("assets", "yellow_dragon.png"))
PURPLE_ENEMY = pygame.image.load(os.path.join("assets", "purple_dragon.png"))
PLAYER_PROJECTILE = pygame.image.load(os.path.join("assets", "player_projectile.png"))
ENEMY_PROJECTILE = pygame.image.load(os.path.join("assets", "enemy_projectile.png"))
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "star_background.png")), (WIDTH, HEIGHT))

# TODO center projectiles with source object
class Projectile:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


# define abstract class for ships(players and enemies use)
class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.dragon_img = None
        self.projectile_img = None
        self.projectiles = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.dragon_img, (self.x, self.y))
        for projectile in self.projectiles:
            projectile.draw(window)

    def move_projectiles(self, vel, obj):
        self.cooldown()
        for projectile in self.projectiles:
            projectile.move(vel)
            if projectile.off_screen(HEIGHT):
                self.projectiles.remove(projectile)
            elif projectile.collision(obj):
                obj.health -= 10
                self.projectiles.remove(projectile)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def get_width(self):
        return self.dragon_img.get_width()

    def get_height(self):
        return self.dragon_img.get_height()

    def shoot(self):
        if self.cool_down_counter == 0:
            projectile = Projectile(self.x, self.y, self.projectile_img)
            self.projectiles.append(projectile)
            self.cool_down_counter = 1


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.dragon_img = PLAYER_DRAGON
        self.projectile_img = PLAYER_PROJECTILE
        # use pygame.mask for pixel perfect collision
        self.mask = pygame.mask.from_surface(self.dragon_img)
        self.max_health = health

    def move_projectiles(self, vel, objs):
        self.cooldown()
        for projectile in self.projectiles:
            projectile.move(vel)
            if projectile.off_screen(HEIGHT):
                self.projectiles.remove(projectile)
            else:
                for obj in objs:
                    if projectile.collision(obj):
                        objs.remove(obj)
                        if projectile in self.projectiles:
                            self.projectiles.remove(projectile)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.dragon_img.get_height() + 10, self.dragon_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.dragon_img.get_height() + 10,
                                               self.dragon_img.get_width() * (self.health / self.max_health), 10))

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)


# TODO give enemies unique projectiles


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_ENEMY, ENEMY_PROJECTILE),
        "purple": (PURPLE_ENEMY, ENEMY_PROJECTILE),
        "yellow": (YELLOW_ENEMY, ENEMY_PROJECTILE)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.dragon_img, self.projectile_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.dragon_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            projectile = Projectile(self.x + 20, self.y, self.projectile_img)
            self.projectiles.append(projectile)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


# the main game loop
def main():
    run = True
    fps = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("Ariel", 50)
    lost_font = pygame.font.SysFont("Ariel", 75)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    # define player speed
    player_vel = 5
    projectile_vel = 5

    player = Player(300, 650)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WINDOW.blit(BG, (0, 0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (0, 255, 150))
        level_label = main_font.render(f"Level: {level}", 1, (0, 255, 150))

        WINDOW.blit(lives_label, (10, 10))
        WINDOW.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        # draw enemies to the screen, above player.draw so that player will be drawn on top
        for enemy in enemies:
            enemy.draw(WINDOW)
        # draw the player object
        player.draw(WINDOW)

        if lost:
            lost_label = lost_font.render("You Lost!", 1, (255, 0, 0))
            WINDOW.blit(lost_label, ((WIDTH / 2 - lost_label.get_width() / 2), 350))

        pygame.display.update()

    while run:
        clock.tick(fps)
        redraw_window()
        if lives <= 0 or player.health == 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > fps * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            # spawn enemies at different heights above the screen and allow them to descend at same velocity
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(["red", "yellow", "purple"]))
                enemies.append(enemy)

        # ends the main game loop when the window is closed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # controls for player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x + player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT:  # down
            player.y += player_vel
        if keys[pygame.K_w] and player.y + player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # right
            player.x += player_vel
        if keys[pygame.K_SPACE]:  # right
            player.shoot()

        # move enemies, [:] creates a copy of the list each loop so that removing enemies that hit bottom doesn't break the list
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_projectiles(projectile_vel, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_projectiles(-projectile_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("Helvetica", 70)
    run = True
    while run:
        WINDOW.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WINDOW.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main()
