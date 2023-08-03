import pygame

from scripts.game import Game
from scripts.menus import MainMenu, OptionsMenu, CreditsMenu, LeaderboardMenu, SignUpMenu, LoginMenu, SelectionMenu
from scripts.utils import create_window, load_data

pygame.init()
pygame.mixer.set_num_channels(16)

# Set up pygame
monitor = pygame.display.Info()
window = create_window((monitor.current_w, monitor.current_h))
fps = 60

data = load_data()
if 'logged_in' in data:
    current_screen = 'main_menu'
else:
    current_screen = 'selection'

screens = {
    'selection': SelectionMenu, 'signup': SignUpMenu, 'login': LoginMenu, 
    'main_menu': MainMenu, 'game': Game, 'options_menu': OptionsMenu, 'leaderboard': LeaderboardMenu, 'credits_menu': CreditsMenu
    }
running = True

while running:
    screen = screens[current_screen](window, fps)
    current_screen = screen.run()
    window = screen.window
    fps = screen.fps
    if current_screen not in screens:
        break

pygame.quit()