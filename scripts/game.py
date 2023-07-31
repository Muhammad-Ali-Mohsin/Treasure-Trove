import time
import random

import pygame

from scripts.utils import load_image, load_images, get_text_surf, format_num
from scripts.maze import generate_maze
from scripts.entities import Player, Enemy
from scripts.animations import load_animation, load_animation_library, AnimationHandler
from scripts.particles import ParticleHandler
from scripts.treasure import Treasure
from scripts.compass import Compass

class Game:
    def __init__(self, window, fps):
        random.seed(0)
        self.kill_screen = False
        self.fps = fps
        self.window = window
        pygame.display.set_caption("Treasure Trove")
        self.display = pygame.Surface((426, 240))
        self.larger_display = pygame.Surface((1280, 720)).convert_alpha()
        self.clock = pygame.time.Clock()

        self.camera_displacement = [0, 0]
        self.dt = 0
        self.last_time = 0
        self.screen_shake = [0, 0]
        self.paused = False
        self.game_over = False

        # Loads all the images in
        self.images = {
            'hedge': load_images("assets/images/hedges"),
            'path': load_images("assets/images/paths"),
            'healthbar': load_image("assets/images/healthbar.png"),
            'gold_pouch': load_image("assets/images/gold_pouch.png"),
            'compass_base': load_image("assets/images/compass_base.png"),
            'compass_spinner': load_image("assets/images/compass_spinner.png"),
            'box': load_image("assets/images/box.png"),
            'grey_screen': pygame.Surface(self.display.get_size())
        }

        # Loads all the animations in
        self.animations = {
            'player': load_animation_library("assets/animations/player"),
            'slime': load_animation_library("assets/animations/slime"),
            'treasure': load_animation_library("assets/animations/treasure"),
            'dirt': {'default': load_animation("assets/particles/dirt", (0.1, 0.1, 0.1), False)},
            'leaves': {'default': load_animation("assets/particles/leaves", (0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1), False)},
            'experience': {'default': load_animation("assets/particles/experience", (0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1), True)},
            'slime_particle': {'default': load_animation("assets/particles/slime", (0.1, 0.1, 0.1, 0.1), False)},
            'dust': {'default': load_animation("assets/particles/dust", (0.1, 0.1, 0.1, 0.1), False)},
            'gold': {'default': load_animation("assets/particles/gold", (0.1, 0.1), True)}
        }

        # Changes the opacity of all the dirt particles to make them somewhat transparent
        for img in self.animations['dirt']['default']['images']:
            img.set_alpha(150)

        # Makes the grey screen transparent
        self.images['grey_screen'].set_alpha(175)

        # Creates the game variables
        self.maze = generate_maze(self, tile_size=32, maze_resolution=(25, 25), removed_tiles=100)
        self.player = Player(self, self.maze.get_random_loc("path"), (14, 20), 2, 100)
        self.enemies = []
        self.treasure = Treasure(self)
        self.gold = 0

        # Graphical variables
        self.compass = Compass(self)
        self.wind_intensity = random.random()
        self.paused_text = get_text_surf(size=40, text="Paused", colour=(172, 116, 27))
        self.game_over_text = get_text_surf(size=30, text="Game Over", colour=(172, 116, 27))

    def create_enemy(self):
        """
        Spawns an enemy in a random location
        """
        self.enemies.append(Enemy(self, self.maze.get_loc(self.player.pos), (16, 16), random.randint(2, 3), 30))
        #self.enemies.append(Enemy(self, self.maze.get_random_loc("path"), (16, 16), random.randint(2, 3), 30))

    def shake_screen(self, magnitude, duration):
        """
        Shakes the screen
        """
        self.screen_shake = [magnitude, duration]

    def handle_events(self):
        """
        Handles all pygame events such as button presses
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.kill_screen = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.moving['left'] = True
                    if self.player.animation.current_animation != "death": self.player.animation.flip = True
                if event.key == pygame.K_RIGHT:
                    self.player.moving['right'] = True
                    if self.player.animation.current_animation != "death": self.player.animation.flip = False
                if event.key == pygame.K_UP:
                    self.player.moving['up'] = True
                if event.key == pygame.K_DOWN:
                    self.player.moving['down'] = True
                if event.key == pygame.K_ESCAPE:
                    self.kill_screen = True
                if event.key == pygame.K_TAB:
                    self.paused = not self.paused
                if event.key == pygame.K_x:
                    if self.player.animation.current_animation != "death": self.player.attack()
                if event.key == pygame.K_1:
                    self.create_enemy()
                if event.key == pygame.K_2:
                    self.treasure.open()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.player.moving['left'] = False
                if event.key == pygame.K_RIGHT:
                    self.player.moving['right'] = False
                if event.key == pygame.K_UP:
                    self.player.moving['up'] = False
                if event.key == pygame.K_DOWN:
                    self.player.moving['down'] = False

    def draw_healthbar(self):
        """
        Draws the healthbar image as as well as the player's health
        """
        pygame.draw.rect(self.display, (255, 0, 0), (28, 14, (self.player.health / 100) * 77, 6))
        self.display.blit(self.images['healthbar'], (5, 5))

    def draw_gold(self):
        """
        Draws the player's gold onto the screen
        """
        gold_text = get_text_surf(size=15, text=f"{format_num(self.gold)} gold", colour=(255, 202, 24))
        self.display.blit(self.images['gold_pouch'], (5, 35))
        self.display.blit(gold_text, (self.images['gold_pouch'].get_width() + 10, 32 + (gold_text.get_height() // 2)))

    def draw_screen(self, text):
        """
        Draws a screen with a given text as the center (Used for the pause screen and game over screen)
        """
        self.display.blit(self.images['grey_screen'], (0, 0))
        self.display.blit(self.images['box'], ((self.display.get_width() // 2) - (self.images['box'].get_width() // 2), (self.display.get_height() // 2) - (self.images['box'].get_height() // 2)))
        self.display.blit(text, ((self.display.get_width() // 2) - (text.get_width() // 2), (self.display.get_height() // 2) - (text.get_height() // 2)))

    def update_display(self):
        """
        Calls all functions to update the display
        """
        # Clears the display
        self.display.fill((35, 72, 39))
        self.larger_display.fill((0, 0, 0, 0))

        self.maze.draw()
        self.treasure.draw()
        ParticleHandler.update()
        self.player.draw()

        for enemy in self.enemies:
            enemy.draw()
 
        self.draw_healthbar()
        self.draw_gold()
        self.compass.draw()

        if self.game_over:
            self.draw_screen(self.game_over_text)
        elif self.paused:
            self.draw_screen(self.paused_text)
        

        screen_shake = (random.random() * self.screen_shake[0], random.random() * self.screen_shake[0]) if self.screen_shake[1] > 0 else (0, 0)
        self.window.blit(pygame.transform.scale(self.display, self.window.get_size()), screen_shake)
        self.window.blit(pygame.transform.scale(self.larger_display, self.window.get_size()), screen_shake)
        #fps_text = get_text_surf(size=55, text=f"FPS: {round(self.clock.get_fps())}", colour=pygame.Color("white"))
        #self.window.blit(fps_text, (10, 10))
        pygame.display.update()

    def run(self):
        """
        Runs the game loop
        """
        while not self.kill_screen:
            if not self.paused and not self.game_over:
                # Calculates the change in time
                self.dt = (time.time() - self.last_time)
                self.last_time = time.time()
                self.multi = self.dt * 60

                # Counts down the screen shake
                self.screen_shake[1] = max(self.screen_shake[1] - self.dt, 0)

                # Randomly changes the wind intensity
                if random.randint(0, 100) == 1:
                    self.wind_intensity = random.random()

                # Spawns leaves from the hedges that are on the screen
                if random.randint(0, 10) == 1:
                    top_left_loc = self.maze.get_loc(self.camera_displacement)
                    bottom_right_loc = self.maze.get_loc((self.camera_displacement[0] + self.display.get_width(), self.camera_displacement[1] + self.display.get_height()))
                    top_left_loc = (max(0, top_left_loc[0]), max(0, top_left_loc[1]))
                    bottom_right_loc = (min(self.maze.resolution[0], bottom_right_loc[0]), min(self.maze.resolution[1], bottom_right_loc[1]))
                    loc = self.maze.get_random_loc("hedge", (top_left_loc, bottom_right_loc))
                    ParticleHandler.create_particle("leaf", self, ((loc[0] * self.maze.tile_size) + (self.maze.tile_size // 2),  (loc[1] * self.maze.tile_size) + (self.maze.tile_size // 4)), speed=random.random() * random.random())
                
                # Updates all animations. This isn't done in update display as some logic relies on the animation states
                AnimationHandler.update(self.dt)

                # Updates the player and the enemies if the player isn't dead
                if not self.player.animation.current_animation == "death":
                    self.player.update()

                    for enemy in self.enemies:
                        enemy.update()

                elif self.player.animation.done:
                    self.game_over = True

                self.treasure.update()
                self.compass.update()

                # Calculates the camera displacement
                self.camera_displacement[0] = int(self.player.pos[0] - (self.display.get_width() // 2))
                self.camera_displacement[1] = int(self.player.pos[1] - (self.display.get_height() // 2))

            self.handle_events()
            self.update_display()
            self.clock.tick(self.fps)

        return "main_menu"