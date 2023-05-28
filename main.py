import pygame, os
from misc import get_options, update_options
pygame.init()

if os.path.exists("assets/options.txt"):
    # Loads the data from the options file
    user_resolution, fps = get_options()
else:
    # Creates new options if options file doesn't exist
    fps = 60
    monitor = pygame.display.Info() # This is the user's physical monitor
    user_resolution = (monitor.current_w, monitor.current_h)
    update_options(user_resolution=user_resolution, fps=fps)

# Set up pygame
window = pygame.display.set_mode(user_resolution)

from variables import ICON_IMG
from game import Game
from main_menu import MainMenu
from menus import OptionsMenu

pygame.mouse.set_visible(False)
pygame.display.set_caption("Treasure Trove")
pygame.display.set_icon(ICON_IMG)

screens = {'main menu': MainMenu, 'options menu': OptionsMenu, 'game': Game}
current_screen = MainMenu(window, fps)

while True:
    # Runs a frame of the current screen
    current_screen.run_frame()
    # Checks whether the selected screen is no longer the current screen
    if current_screen.screentype != current_screen.selected_screen:
        # Checks whether the newly selected screen exists
        if current_screen.selected_screen in screens:
            # Changes the window and fps to the current screen's window and fps in case they were changed
            if current_screen.screentype == "options menu":
                window = current_screen.window
                fps = current_screen.fps
            # Changes the current screen to the newly selected screen
            current_screen = screens[current_screen.selected_screen](window, fps)
        else:
            # Exits the game
            pygame.display.quit()
            break