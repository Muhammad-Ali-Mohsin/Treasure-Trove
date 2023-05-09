import pygame
pygame.init()
from variables import *
from game import Game

# Set up pygame
pygame.mouse.set_visible(False)
pygame.display.set_caption("Treasure Trove")
pygame.display.set_icon(ICON_IMG)


game = Game()

while True:
    game.game_loop()