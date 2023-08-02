import pygame

from scripts.game import Game
from scripts.menus import MainMenu, OptionsMenu
from scripts.utils import create_window

pygame.init()
pygame.mixer.set_num_channels(16)

# Set up pygame
monitor = pygame.display.Info()
window = create_window((monitor.current_w, monitor.current_h))
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