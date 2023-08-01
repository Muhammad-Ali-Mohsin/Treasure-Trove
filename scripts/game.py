import time
import random

import pygame

from scripts.utils import load_image, load_images, get_text_surf, format_num, AudioPlayer
from scripts.maze import generate_maze
from scripts.entities import Player, Enemy
from scripts.animations import load_animation, load_animation_library, AnimationHandler
from scripts.particles import ParticleHandler
from scripts.treasure import Treasure
from scripts.compass import Compass

TRANSITION_DURATION = 1

class Game:
    def __init__(self, window, fps):
        random.seed(0)
        pygame.display.set_caption("Treasure Trove")
        self.kill_screen = False
        self.fps = fps
        self.window = window
        self.display = pygame.Surface((426, 240))
        self.larger_display = pygame.Surface((1280, 720)).convert_alpha()
        self.clock = pygame.time.Clock()

        # Variables about the transition
        self.transition_surf = pygame.Surface(self.larger_display.get_size())
        self.transition_surf.set_colorkey((255, 255, 255))
        self.transition_surf.fill((255, 255, 255))
        self.transition_timer = 0
        self.end_transition = False

        # Variables about the camera
        self.camera_displacement = [0, 0]
        self.dt = 0
        self.last_time = time.time()
        self.screen_shake = [0, 0]

        # Loads all the images in
        self.images = {
            'hedge': load_images("assets/images/hedges"),
            'path': load_images("assets/images/paths"),
            'healthbar': load_image("assets/images/healthbar.png"),
            'gold_pouch': load_image("assets/images/gold_pouch.png"),
            'compass_base': load_image("assets/images/compass_base.png"),
            'compass_spinner': load_image("assets/images/compass_spinner.png"),
            'box': load_image("assets/images/box.png"),
            'grey_screen': pygame.Surface(self.larger_display.get_size()).convert_alpha()
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
            'gold': {'default': load_animation("assets/particles/gold", (0.1, 0.1), True)},
            'bee': {'default': load_animation("assets/particles/bee", (0.1, 0.1, 0.1), True)}
        }

        # Image rescaling
        self.images['compass_spinner'] = pygame.transform.scale(self.images['compass_spinner'], (self.images['compass_spinner'].get_width() * 3, self.images['compass_spinner'].get_height() * 3))
        self.images['box'] = pygame.transform.scale(self.images['box'], (self.images['box'].get_width() * 3, self.images['box'].get_height() * 3))

        # Changes transparency
        for img in self.animations['dirt']['default']['images']:
            img.set_alpha(150)
        self.images['grey_screen'].set_alpha(175)

        # Variables about the game
        self.maze = generate_maze(self, tile_size=32, maze_resolution=(25, 25), removed_tiles=25)
        self.player = Player(self, self.maze.get_random_loc("path"), (14, 20), 2, 100)
        self.enemies = []
        self.treasure = Treasure(self)
        self.gold = 0
        self.wave = 0
        self.killed = 0
        self.paused = False
        self.game_over = False

        # Graphical variables
        self.compass = Compass(self)
        self.wind_intensity = random.random()
        self.text_updated = False
        self.text = {
            'paused': get_text_surf(size=70, text="Paused", colour=(172, 116, 27)), 
            'game_over': get_text_surf(size=70, text="Game Over", colour=(172, 116, 27)),
            'return': get_text_surf(size=20, text="Press Backspace to return to Main Menu", colour=(172, 116, 27)),
            'wave_label': get_text_surf(size=30, text=f"Wave:", colour=(172, 116, 27)),
            'killed_label': get_text_surf(size=30, text=f"Enemies Killed:", colour=(172, 116, 27)),
            'remaining_label': get_text_surf(size=30, text=f"Enemies Remaining:", colour=(172, 116, 27)),
            'gold_label': get_text_surf(size=30, text=f"Gold collected:", colour=(172, 116, 27))
            }
        self.update_text()

        # Audio
        music = pygame.mixer.Sound("assets/sfx/music.wav")
        music.set_volume(0.7)
        music.play(-1, fade_ms=1000)
        ambience = pygame.mixer.Sound("assets/sfx/ambience.wav")
        ambience.play(-1, fade_ms=1000)
        AudioPlayer.load_sounds("running", "assets/sfx/running", 0.2, True)
        AudioPlayer.load_sounds("enemy_attack", "assets/sfx/enemy_attack", 0.8, True)
        AudioPlayer.load_sound("health", "assets/sfx/health.wav", 0.7)
        AudioPlayer.load_sound("gold", "assets/sfx/gold.wav", 0.7)
        AudioPlayer.load_sound("player_attack", "assets/sfx/player_attack.wav", 0.8)
        AudioPlayer.load_sound("enemy_death", "assets/sfx/enemy_death.wav", 1)
        AudioPlayer.load_sound("treasure", "assets/sfx/treasure.wav", 0.4)
        AudioPlayer.load_sound("experience", "assets/sfx/experience.wav", 0.3)
        AudioPlayer.load_sound("hit", "assets/sfx/hit.wav", 1)


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
                    self.paused = not self.paused
                if event.key == pygame.K_BACKSPACE:
                    if self.paused or self.game_over: 
                        self.transition_timer = -TRANSITION_DURATION
                        self.end_transition = True
                if event.key == pygame.K_x:
                    if self.player.animation.current_animation != "death": self.player.attack()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.player.moving['left'] = False
                if event.key == pygame.K_RIGHT:
                    self.player.moving['right'] = False
                if event.key == pygame.K_UP:
                    self.player.moving['up'] = False
                if event.key == pygame.K_DOWN:
                    self.player.moving['down'] = False

    def create_enemy(self):
        """
        Spawns an enemy in a random location
        """
        self.enemies.append(Enemy(self, self.maze.get_random_loc("path"), (16, 16), (random.random()) + 1, 30))

    def spawn_enemies(self):
        """
        Spawns a bunch of enemies based on the current wave
        """
        for i in range(round(self.wave / 1.5)):
            self.create_enemy()

    def shake_screen(self, magnitude, duration):
        """
        Shakes the screen
        """
        self.screen_shake = [magnitude, duration]

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
        # Draws the grey screen, the box, the return to menu text and the title text
        self.larger_display.blit(self.images['grey_screen'], (0, 0))
        box_pos = ((self.larger_display.get_width() // 2) - (self.images['box'].get_width() // 2), (self.larger_display.get_height() // 2) - (self.images['box'].get_height() // 2))
        self.larger_display.blit(self.images['box'], box_pos)
        self.larger_display.blit(text, ((self.larger_display.get_width() // 2) - (text.get_width() // 2), (self.larger_display.get_height() // 2) - (text.get_height() // 2) - 80))
        self.larger_display.blit(self.text['return'], ((self.larger_display.get_width() // 2) - (self.text['return'].get_width() // 2), (self.larger_display.get_height() // 2) - (self.text['return'].get_height() // 2) + 120))

        # Draws the metrics onto the screen
        for i, metric in enumerate(('wave', 'killed', 'remaining', 'gold')):
            self.larger_display.blit(self.text[metric + '_label'], (box_pos[0] + 100, (self.larger_display.get_height() // 2) - (self.text[metric + '_label'].get_height() // 2) + (i * 30) - 20))
            self.larger_display.blit(self.text[metric], (box_pos[0] + self.images['box'].get_width() - (self.text[metric].get_width() // 2) - 100, (self.larger_display.get_height() // 2) - (self.text[metric].get_height() // 2) + (i * 30) - 20))

    def update_text(self):
        """
        Updates the text surfaces that are drawn during the pause and game over screens
        """
        self.text['wave'] = get_text_surf(size=30, text=str(self.wave), colour=(172, 116, 27))
        self.text['killed'] = get_text_surf(size=30, text=str(self.killed), colour=(172, 116, 27))
        self.text['remaining'] = get_text_surf(size=30, text=str(len(self.enemies)), colour=(172, 116, 27))
        self.text['gold'] = get_text_surf(size=30, text=format_num(self.gold), colour=(172, 116, 27))

    def update_display(self):
        """
        Calls all functions to update the display
        """
        # Clears the display
        self.display.fill((35, 72, 39))
        self.larger_display.fill((0, 0, 0, 0))

        # Draws all maze elements
        self.maze.draw()
        self.treasure.draw()

        # Updates and draws the particles
        ParticleHandler.update()

        # Draws all entities
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
 
        # Draws the HUD
        self.draw_healthbar()
        self.draw_gold()
        self.compass.draw()

        # Draws the game over and paused screens
        if self.game_over:
            self.draw_screen(self.text['game_over'])
        elif self.paused:
            self.draw_screen(self.text['paused'])

        # Draws the transition
        if self.transition_timer != TRANSITION_DURATION:
            self.transition_surf.fill((0, 0, 0))
            pygame.draw.circle(self.transition_surf, (255, 255, 255), (self.transition_surf.get_width() // 2, self.transition_surf.get_height() // 2), ((self.transition_surf.get_width() * 3/4) * (abs(self.transition_timer) / TRANSITION_DURATION)))

        # Blits the transition surface onto the larger surf and then both surfaces onto the window
        self.larger_display.blit(self.transition_surf, (0, 0))
        screen_shake = (random.random() * self.screen_shake[0], random.random() * self.screen_shake[0]) if self.screen_shake[1] > 0 else (0, 0)
        self.window.blit(pygame.transform.scale(self.display, self.window.get_size()), screen_shake)
        self.window.blit(pygame.transform.scale(self.larger_display, self.window.get_size()), screen_shake)
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
            if not self.paused and not self.game_over:

                # Plays the running sound if the player is running
                if self.player.moving['right'] or self.player.moving['left'] or self.player.moving['up'] or self.player.moving['down']:
                    AudioPlayer.play_sound("running")

                # Sets the text to not updated as the game is not paused
                if self.text_updated: self.text_updated = False

                # Counts down the screen shake
                self.screen_shake[1] = max(self.screen_shake[1] - self.dt, 0)

                # Randomly changes the wind intensity
                if random.random() < 0.01:
                    self.wind_intensity = random.random()

                # Spawns leaves from the hedges that are on the screen
                if random.random() < 0.1:
                    top_left_loc = self.maze.get_loc(self.camera_displacement)
                    bottom_right_loc = self.maze.get_loc((self.camera_displacement[0] + self.display.get_width(), self.camera_displacement[1] + self.display.get_height()))
                    top_left_loc = (max(0, top_left_loc[0]), max(0, top_left_loc[1]))
                    bottom_right_loc = (min(self.maze.resolution[0], bottom_right_loc[0]), min(self.maze.resolution[1], bottom_right_loc[1]))
                    loc = self.maze.get_random_loc("hedge", (top_left_loc, bottom_right_loc))
                    if random.random() < 0.1:
                        ParticleHandler.create_particle("bee", self, ((loc[0] * self.maze.tile_size) + (self.maze.tile_size // 2),  (loc[1] * self.maze.tile_size) + (self.maze.tile_size // 4)), speed=random.random() * 0.25 + 0.1)
                    else:
                        ParticleHandler.create_particle("leaf", self, ((loc[0] * self.maze.tile_size) + (self.maze.tile_size // 2),  (loc[1] * self.maze.tile_size) + (self.maze.tile_size // 4)), speed=random.random() * random.random())
                


                # Updates all animations. This isn't done in update display as some logic relies on the animation states
                AnimationHandler.update(self.dt)

                # Updates the player and the enemies if the player isn't dead
                if not self.player.animation.current_animation == "death":
                    self.player.update()

                    for enemy in self.enemies:
                        enemy.update()

                # Ends the game if the player's death animation is over
                elif self.player.animation.done:
                    self.game_over = True

                self.treasure.update()
                self.compass.update()

                # Calculates the camera displacement
                self.camera_displacement[0] = int(self.player.pos[0] - (self.display.get_width() // 2))
                self.camera_displacement[1] = int(self.player.pos[1] - (self.display.get_height() // 2))

            # Runs after the game ends or the game is paused and updates the text
            elif not self.text_updated:
                self.update_text()
                self.text_updated = True

            # Decrements the transition timer and draws the transition   
            self.transition_timer = min(self.transition_timer + self.dt, TRANSITION_DURATION)

            # Ends the screen if the transition is over
            if self.transition_timer >= 0 and (self.game_over or self.paused) and self.end_transition:
                self.kill_screen = True

            self.handle_events()
            self.update_display()
            self.clock.tick(self.fps)

        # Kills all animations, particles and sounds and then returns to the main menu once the game loop has finished
        for particle in ParticleHandler.particles.copy():
            ParticleHandler.kill_particle(particle)
        for animation in AnimationHandler.animations.copy():
            AnimationHandler.kill_animation(animation)
        pygame.mixer.stop()
        return "main_menu"