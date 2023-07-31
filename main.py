import os

import pygame

from scripts.game import Game
from scripts.main_menu import MainMenu
from scripts.options_menu import OptionsMenu
from scripts.utils import load_image

pygame.init()

# This changes the app id for the current process so it isn't grouped under python processes and shows the game on the taskbar by itself
if os.name == "nt": # Checks if the os is windows
    from ctypes import windll
    appid = u"muhammadalimohsin.treasuretrove"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

# Set up pygame
window = pygame.display.set_mode((1920, 1080))
fps = 60

pygame.mouse.set_visible(False)
pygame.display.set_caption("Treasure Trove")
pygame.display.set_icon(load_image("assets/images/icon.png"))

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