import time
import random

import pygame

from scripts.utils import load_image, load_images, get_text_surf
from scripts.maze import generate_maze
from scripts.entities import Player, Enemy
from scripts.animations import load_animation, load_animation_library, AnimationHandler
from scripts.particles import ParticleHandler

random.seed(0)

class Game:
    def __init__(self):
        pygame.init()
        self.kill_screen = False
        self.window = pygame.display.set_mode((1920, 1080))
        pygame.display.set_caption("Treasure Trove")
        self.display = pygame.Surface((426, 240))
        self.clock = pygame.time.Clock()

        self.camera_displacement = [0, 0]
        self.dt = 0
        self.last_time = 0
        self.screen_shake = [0, 0]

        # Loads all the images in
        self.images = {
            'hedge': load_images("assets/images/hedges"),
            'path': load_images("assets/images/paths"),
            'healthbar': load_image("assets/images/healthbar.png")
        }

        # Loads all the animations in
        self.animations = {
            'player': load_animation_library("assets/animations/player"),
            'slime': load_animation_library("assets/animations/slime"),
            'dirt': {'default': load_animation("assets/particles/dirt", (0.1, 0.1, 0.1), False)},
            'leaves': {'default': load_animation("assets/particles/leaves", (0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1), False)},
            'experience': {'default': load_animation("assets/particles/experience", (0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1), True)},
            'slime_particle': {'default': load_animation("assets/particles/slime", (0.1, 0.1, 0.1, 0.1), False)},
            'dust': {'default': load_animation("assets/particles/dust", (0.1, 0.1, 0.1, 0.1), False)}
        }

        # Changes the opacity of all the dirt particles to make them somewhat transparent
        for img in self.animations['dirt']['default']['images']:
            img.set_alpha(150)

        # Creates the game variables
        self.maze = generate_maze(self, tile_size=32, maze_resolution=(40, 40), removed_tiles=100)
        self.player = Player(self, self.maze.get_random_loc("path"), (14, 20), 2, 100)
        self.enemies = []

        # Graphical variables
        self.wind_intensity = random.random()

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
                if event.key == pygame.K_x:
                    if self.player.animation.current_animation != "death": self.player.attack()
                if event.key == pygame.K_1:
                    self.create_enemy()
                if event.key == pygame.K_2:
                    self.shake_screen(5, 0.2)
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

    def update_display(self):
        """
        Calls all functions to update the display
        """
        # Clears the display
        self.display.fill((35, 72, 39))

        self.maze.draw()
        ParticleHandler.update()
        self.player.draw()

        for enemy in self.enemies:
            enemy.draw()
 
        self.draw_healthbar()

        if self.screen_shake[1] > 0:
            screen_shake = (random.random() * self.screen_shake[0], random.random() * self.screen_shake[0])
        else:
            screen_shake = (0, 0)
        self.window.blit(pygame.transform.scale(self.display, self.window.get_size()), screen_shake)
        fps_text = get_text_surf(size=55, text=f"FPS: {round(self.clock.get_fps())}", colour=pygame.Color("white"))
        self.window.blit(fps_text, (10, 10))
        pygame.display.update()

    def run(self):
        """
        Runs the game loop
        """
        while not self.kill_screen:
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

            # Calculates the camera displacement
            self.camera_displacement[0] = int(self.player.pos[0] - (self.display.get_width() // 2))
            self.camera_displacement[1] = int(self.player.pos[1] - (self.display.get_height() // 2))

            self.handle_events()
            self.update_display()
            self.clock.tick(60)


game = Game()
game.run()
pygame.quit()