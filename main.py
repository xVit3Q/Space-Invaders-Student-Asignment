import pygame
import os
import sys
import random
from button import Button
from slider import Slider
import pickle

pygame.init()

pygame.font.init()

WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

# Initialize music and play it
pygame.mixer.music.load('assets/mess.wav')
pygame.mixer.music.play(-1)

# Load and scale background image
BG_main = pygame.image.load("assets/Background-black2.jpg")
scaled_bg = pygame.transform.scale(BG_main, (WIDTH, HEIGHT))
pygame.display.set_caption("Space Invader Knockoff")

# Initialize lost counter
lost_counter = 0

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Function to save options to a file


def save_options(volume, difficulty):
    options = {'volume': volume, 'difficulty': difficulty}
    with open('options.pkl', 'wb') as f:
        pickle.dump(options, f)

# Function to load options from a file


def load_options():
    try:
        with open('options.pkl', 'rb') as f:
            options = pickle.load(f)
        return options.get('volume', 50), options.get('difficulty', 3)  # Default values if file doesn't exist
    except FileNotFoundError:
        return 50, 3


def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)


def play():
    global lost_counter

    # Powerups
    SPEED_POWERUP = pygame.image.load(os.path.join("assets/szybkosc_small.png"))
    UPGRADE_POWERUP = pygame.image.load(os.path.join("assets/gwiazdeczka_small.png"))
    COOLDOWN_POWERUP = pygame.image.load(os.path.join("assets/zegareczek_small.png"))
    RESTORE_POWERUP = pygame.image.load(os.path.join("assets/serduszko_small.png"))

    # Load images
    RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pink-alien1.png"))
    GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "green-alien1.png"))
    BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "blue-alien1.png"))

    # Player
    YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "ship2.png"))
    BETTER_SPACE_SHIP2 = pygame.image.load((os.path.join("assets/ship1.png")))

    # Lasers
    RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
    GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
    BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
    YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

    # Health
    health_image = {
        5: pygame.image.load(os.path.join('assets/SpaceInvaders_Health1.3.png')),
        4: pygame.image.load(os.path.join('assets/SpaceInvaders_Health2.3.png')),
        3: pygame.image.load(os.path.join('assets/SpaceInvaders_Health3.3.png')),
        2: pygame.image.load(os.path.join('assets/SpaceInvaders_Health4.3.png')),
        1: pygame.image.load(os.path.join('assets/SpaceInvaders_Health5.3.png')),
        0: pygame.image.load(os.path.join('assets/SpaceInvaders_Health6.3.png'))
    }

    def display_lives(num_lives):
        if num_lives in health_image:
            WIN.blit(health_image[num_lives], (90, 15))

    # Background
    BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "2567.jpg")), (WIDTH, HEIGHT))

    class Laser:
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
            return not (height >= self.y >= 0)

        def collision(self, obj):
            return collide(self, obj)

    class Ship:
        COOLDOWN = 30

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
            for laser in self.lasers:
                laser.draw(window)

        def move_lasers(self, vel, obj):
            self.cooldown()
            for laser in self.lasers:
                laser.move(vel)
                if laser.off_screen(HEIGHT):
                    self.lasers.remove(laser)
                elif laser.collision(obj):
                    obj.health -= 10
                    self.lasers.remove(laser)

        def cooldown(self):
            if self.cool_down_counter >= self.COOLDOWN:
                self.cool_down_counter = 0
            elif self.cool_down_counter > 0:
                self.cool_down_counter += 1

        def shoot(self):
            if self.cool_down_counter == 0:
                laser = Laser(self.x, self.y - 40, self.laser_img)
                self.lasers.append(laser)
                self.cool_down_counter = 1

        def get_width(self):
            return self.ship_img.get_width()

        def get_height(self):
            return self.ship_img.get_height()

    class Player(Ship):
        def __init__(self, x, y, health=100):
            super().__init__(x, y, health)
            self.ship_img = YELLOW_SPACE_SHIP
            self.laser_img = YELLOW_LASER
            self.mask = pygame.mask.from_surface(self.ship_img)
            self.max_health = health
            self.evolve = 0

        def ship_upgrade(self):
            self.ship_img = BETTER_SPACE_SHIP2

        def move_lasers(self, vel, objs, powerups):  # Add objs and powerups parameters
            self.cooldown()
            for laser in self.lasers[:]:  # Iterate over a copy of self.lasers
                laser.move(vel)
                if laser.off_screen(HEIGHT):
                    self.lasers.remove(laser)
                else:
                    for obj in objs[:]:  # Iterate over a copy of objs
                        if laser.collision(obj):
                            obj.delete(powerups)
                            if laser in self.lasers:
                                self.lasers.remove(laser)
                            if obj in objs:
                                objs.remove(obj)

        def health_bar(self, window):
            pygame.draw.rect(window, (255, 0, 0),
                             (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
            pygame.draw.rect(window, (0, 255, 0),
                             (self.x, self.y + self.ship_img.get_height() + 10,
                              self.ship_img.get_width() * (1 - ((self.max_health - self.health) / self.max_health)),
                              10))

        def draw(self, window):
            super().draw(window)
            self.health_bar(window)

    class Enemy(Ship):
        COLOR_MAP = {
            "red": (RED_SPACE_SHIP, RED_LASER),
            "green": (GREEN_SPACE_SHIP, GREEN_LASER),
            "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
        }

        def __init__(self, x, y, color, health=100):
            super().__init__(x, y, health)
            self.ship_img, self.laser_img = self.COLOR_MAP[color]
            self.mask = pygame.mask.from_surface(self.ship_img)

        def move(self, vel):
            self.y += vel

        def shoot(self):
            if self.cool_down_counter == 0:
                laser = Laser(self.x - 20, self.y, self.laser_img)
                self.lasers.append(laser)
                self.cool_down_counter = 1

        def delete(self, powerups):
            chance = random.random()
            if chance < 0.50:
                powerup_type = random.choice(['heart', 'cooldown', 'upgrade', 'speedup'])
                powerup = PowerUp(self.x, self.y, powerup_type)
                powerups.append(powerup)

    class PowerUp:
        POWER_MAP = {
            "heart": RESTORE_POWERUP,
            "cooldown": COOLDOWN_POWERUP,
            "upgrade": UPGRADE_POWERUP,
            "speedup": SPEED_POWERUP
        }

        def __init__(self, x, y, powerup_type):
            self.x = x
            self.y = y
            self.type = powerup_type
            try:
                self.power_img = self.POWER_MAP[powerup_type]
            except KeyError:
                raise ValueError(f"Invalid powerup type: {powerup_type}")
            self.mask = pygame.mask.from_surface(self.power_img)

        def draw(self, window):
            window.blit(self.power_img, (self.x, self.y))

        def move(self, vel):
            self.y += vel

        def off_screen(self, height):
            return self.y > height

        def collision(self, obj):
            return collide(self, obj)

    def collide(obj1, obj2):
        offset_x = obj2.x - obj1.x
        offset_y = obj2.y - obj1.y
        return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None

    def main():
        global lost_counter
        run = True
        FPS = 60
        level = 0
        lives = 5

        main_font = pygame.font.SysFont("comicsans", 30)
        lost_font = pygame.font.SysFont("comicsans", 60)

        enemies = []
        powerups = []
        wave_length = 5
        enemy_vel = 2
        player_vel = 5
        laser_vel = 5
        powerup_vel = 1

        player = Player(WIDTH / 2, 630)
        evolve = 0
        clock = pygame.time.Clock()

        lost = False
        lost_count = 0

        def redraw_window():
            WIN.blit(BG, (0, 0))
            # draw text
            lives_label = main_font.render("Lives: ", 1, (255, 255, 255))
            display_lives(lives)
            if level == 1:
                level_label = main_font.render("Boss Level", 1, (255, 255, 255))
            else:
                level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

            WIN.blit(lives_label, (0, 0))
            WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

            player.draw(WIN)
            for enemy in enemies:
                enemy.draw(WIN)
            for powerup in powerups:
                powerup.draw(WIN)
            if lost:
                lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
                WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

            pygame.display.update()

        while run:
            clock.tick(FPS)
            redraw_window()

            if lives <= 0 or player.health <= 0:
                lost = True
                lost_count += 1

            if lost:
                lost_counter += 1
                if lost_count > FPS * 3:

                    run = False

                else:
                    continue

            if len(enemies) == 0:
                level += 1
                wave_length += 5
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                                  random.choice(["red", "blue", "green"]))
                    enemies.append(enemy)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] and player.x - player_vel > 0:  # left
                player.x -= player_vel
            if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # right
                player.x += player_vel
            if keys[pygame.K_w] and player.y - player_vel > 0:  # up
                player.y -= player_vel
            if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:  # down
                player.y += player_vel
            if keys[pygame.K_SPACE]:
                player.shoot()

            for enemy in enemies[:]:
                enemy.move(enemy_vel)
                enemy.move_lasers(laser_vel, player)

                if random.randrange(1, 3 * 30) == 1:
                    enemy.shoot()

                if collide(enemy, player):
                    player.health -= 10
                    enemies.remove(enemy)
                elif enemy.y + enemy.get_height() > HEIGHT:
                    lives -= 1
                    enemies.remove(enemy)
            for powerup in powerups[:]:
                powerup.move(powerup_vel)
                if powerup.off_screen(HEIGHT):
                    powerups.remove(powerup)
                elif powerup.collision(player):
                    if powerup.type == 'heart':
                        player.health += 20
                    elif powerup.type == 'speedup':
                        player_vel += 1
                    elif powerup.type == "cooldown":
                        Player.COOLDOWN -= 5
                    elif powerup.type == 'upgrade':
                        evolve += 1
                        if evolve >= 3:
                            player.ship_upgrade()
                    powerups.remove(powerup)

            player.move_lasers(-laser_vel, enemies, powerups)





    main()


def options():

    def display_difficulty_label(window, difficulty, x, y):
        difficulty_label_font = get_font(30)
        difficulty_levels = {
            5: "Impossible",
            4: "Hell",
            3: "Nightmare",
            2: "Medium",
            1: "Easy"
        }
        rounded_difficulty = round(difficulty)
        if rounded_difficulty < 1:
            rounded_difficulty = 1
        elif rounded_difficulty > 5:
            rounded_difficulty = 5

        difficulty_text = difficulty_levels[rounded_difficulty]
        difficulty_label = difficulty_label_font.render(f"Difficulty: {difficulty_text}", 1, (255, 255, 255))
        text_width = difficulty_label.get_width()
        text_x = (WIDTH - text_width) // 2  # Center the text horizontally
        window.blit(difficulty_label, (text_x, y))

    volume, difficulty = load_options()
    volume_slider = Slider(730, 270, 400, 0, 100, volume)
    difficulty_slider = Slider(150, 270, 300, 1, 5, difficulty)

    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()
        WIN.blit(scaled_bg, (0, 0))
        OPTIONS_TEXT = get_font(100).render("OPTIONS", 1, "#b68f40")

        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(WIDTH / 2, 100))
        WIN.blit(OPTIONS_TEXT, OPTIONS_RECT)
        OPTIONS_BACK = Button(image=None, pos=(640, 660),
                              text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")
        OPTIONS_BACK.change_color(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(WIN)

        DIFFICULTY_TEXT = get_font(50).render("DIFFICULTY", 1, "#d8d480")
        DIFFICULTY_RECT = DIFFICULTY_TEXT.get_rect(center=(WIDTH / 2 - 350, 200))
        WIN.blit(DIFFICULTY_TEXT, DIFFICULTY_RECT)

        VOLUME_TEXT = get_font(50).render("MUSIC VOLUME", 1, "#d8d480")
        VOLUME_RECT = VOLUME_TEXT.get_rect(center=(WIDTH / 2 + 300, 200))
        WIN.blit(VOLUME_TEXT, VOLUME_RECT)

        volume_slider.draw(WIN)
        difficulty_slider.draw(WIN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            volume_slider.update(event)
            difficulty_slider.update(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.check_for_input(OPTIONS_MOUSE_POS):
                    save_options(volume_slider.get_value(), difficulty_slider.get_value())
                    main_menu()

        volume = volume_slider.get_value() / 100  # Get the volume as a percentage
        pygame.mixer.music.set_volume(volume)  # Adjust the volume

        difficulty = difficulty_slider.get_value()
        display_difficulty_label(WIN, difficulty, 350, 350)

        pygame.display.update()


def main_menu():
    global lost_counter
    while True:
        WIN.blit(scaled_bg, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))
        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(640, 250),
                             text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="RED")
        if lost_counter > 0:
            PLAY_BUTTON = Button.create_button_with_scaled_image("assets/Play Rect.png", "PLAY AGAIN",
                                                                 (640, 250), font=get_font(75), base_color="#d7fcd4",
                                                                 hovering_color="RED")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 400),
                                text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="RED")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 550),
                             text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="RED")

        WIN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.change_color(MENU_MOUSE_POS)
            button.update(WIN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.check_for_input(MENU_MOUSE_POS):
                    play()
                if OPTIONS_BUTTON.check_for_input(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.check_for_input(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()


main_menu()