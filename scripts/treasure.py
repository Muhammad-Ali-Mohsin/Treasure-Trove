import random
import math

import pygame

from scripts.animations import AnimationHandler
from scripts.particles import ParticleHandler
from scripts.utils import AudioPlayer

class Treasure:
    def __init__(self, game):
        self.game = game
        self.loc = None
        self.animation = AnimationHandler.create_animation()
        self.animation.change_animation_library(self.game.animations['treasure'])
        self.released_gold = False
        self.reset()
    
    def get_rect(self):
        return pygame.Rect((self.loc[0] * self.game.maze.tile_size) + 8, (self.loc[1] * self.game.maze.tile_size) + 8, 16, 16)

    def reset(self):
        top_left_loc = self.game.maze.get_loc(self.game.camera_displacement)
        bottom_right_loc = self.game.maze.get_loc((self.game.camera_displacement[0] + self.game.display.get_width(), self.game.camera_displacement[1] + self.game.display.get_height()))
        top_left_loc = (max(0, top_left_loc[0]), max(0, top_left_loc[1]))
        bottom_right_loc = (min(self.game.maze.resolution[0], bottom_right_loc[0]), min(self.game.maze.resolution[1], bottom_right_loc[1]))
        loc = self.game.maze.get_random_loc("path", (top_left_loc, bottom_right_loc), 'outside')
        self.loc = loc
        self.animation.change_animation("closed")

    def open(self):
        self.game.shake_screen(10, 0.3)
        self.animation.change_animation("open")
        AudioPlayer.play_sound("chest")

    def update(self):
        if self.animation.current_animation == "open" and self.animation.frame == len(self.animation.animation_library[self.animation.current_animation]['images']) - 1 and not self.released_gold:
            for i in range(10):
                ParticleHandler.create_particle("gold", self.game, ((self.loc[0] * self.game.maze.tile_size) + 8 + random.randint(-5, 5), (self.loc[1] * self.game.maze.tile_size) + 8 + random.randint(-5, 5)), velocity=(random.uniform(2, -2), random.uniform(-4, -2)))
            self.released_gold = True
        if self.animation.current_animation == "open" and self.animation.done:
            # Creates dust particles which fly off the treasure to show it's disappearing
            for angle in (math.pi * 1/4, math.pi * 2/4, math.pi * 3/4, math.pi, math.pi * 5/4, math.pi * 6/4, math.pi * 7/4, math.pi * 8/4):
                ParticleHandler.create_particle("dust", self.game, ((self.loc[0] * self.game.maze.tile_size) + 8, (self.loc[1] * self.game.maze.tile_size) + 8), speed=random.uniform(1, 2), angle=angle)
 
            self.reset()
            self.released_gold = False
            self.game.wave += 1
            self.game.special_attacks = [5, 5, 5]

    def draw(self):
        img = self.animation.get_img()
        pos = ((self.loc[0] * self.game.maze.tile_size) - self.game.camera_displacement[0], (self.loc[1] * self.game.maze.tile_size) - self.game.camera_displacement[1])
        self.game.display.blit(img, pos)
