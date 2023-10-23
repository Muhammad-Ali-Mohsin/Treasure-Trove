import math

import pygame

WIDTH_MULTI = 0.75
HEIGHT_MULTI = 3

class Spike:
    def __init__(self, game, pos, angle, speed, color, can_damage=False):
        self.game = game
        self.pos = list(pos)
        self.timer = None
        self.angle = angle
        self.speed = speed
        self.color = color
        self.can_damage = can_damage

    def get_rect(self):
        return pygame.Rect(*self.pos, self.speed * HEIGHT_MULTI, self.speed * HEIGHT_MULTI)

    def update(self):
        self.pos[0] += math.cos(self.angle) * self.speed * self.game.multi
        self.pos[1] += math.sin(self.angle) * self.speed * self.game.multi
        self.speed -= self.game.dt * 3
        if self.can_damage:
            rect = self.get_rect()
            for enemy in self.game.enemies:
                if rect.colliderect(enemy.get_rect()):
                    enemy.hit()

    def draw(self):
        """
        Draws the spike onto the display
        """
        pos = (self.pos[0] - self.game.camera_displacement[0], self.pos[1] - self.game.camera_displacement[1])
        pygame.draw.polygon(self.game.display, self.color, [
            (pos[0] + math.cos(self.angle) * self.speed * HEIGHT_MULTI, pos[1] + math.sin(self.angle) * self.speed * HEIGHT_MULTI),
            (pos[0] + math.cos(self.angle + math.pi * 0.5) * self.speed * WIDTH_MULTI, pos[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * WIDTH_MULTI),
            (pos[0] + math.cos(self.angle + math.pi) * self.speed * HEIGHT_MULTI, pos[1] + math.sin(self.angle + math.pi) * self.speed * HEIGHT_MULTI),
            (pos[0] + math.cos(self.angle - math.pi * 0.5) * self.speed * WIDTH_MULTI, pos[1] + math.sin(self.angle - math.pi * 0.5) * self.speed * WIDTH_MULTI),
        ])