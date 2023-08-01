import os

import pygame

from scripts.game import Game
from scripts.main_menu import MainMenu
from scripts.options_menu import OptionsMenu
from scripts.utils import load_image, create_window

pygame.init()
pygame.mixer.set_num_channels(32)

# Set up pygame
window = create_window((1920, 1080))
fps = 60

screens = {'main_menu': MainMenu, 'game': Game, 'options_menu': OptionsMenu}
current_screen = 'main_menu'
running = True

while running:
    screen = screens[current_screen](window, fps)
    current_screen = screen.run()
    window = screen.window
    fps = screen.fps
    if current_screen not in screens:
        break

pygame.quit()