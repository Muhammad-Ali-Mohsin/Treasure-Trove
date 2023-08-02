import random
import math

import pygame

from scripts.particles import ParticleHandler
from scripts.animations import AnimationHandler
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
        self.loc = self.game.maze.get_random_loc("path")
        self.animation.change_animation("closed")

    def open(self):
        self.animation.change_animation("open")

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
            self.game.spawn_enemies()

    def draw(self):
        img = self.animation.get_img()
        pos = ((self.loc[0] * self.game.maze.tile_size) - self.game.camera_displacement[0], (self.loc[1] * self.game.maze.tile_size) - self.game.camera_displacement[1])
        self.game.display.blit(img, pos)
