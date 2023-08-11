import pygame

from scripts.game import Game
from scripts.menus import MainMenu, OptionsMenu, CreditsMenu, LeaderboardMenu, SignUpMenu, LoginMenu, SelectionMenu
from scripts.utils import create_window, load_data

pygame.init()
pygame.mixer.set_num_channels(32)

# Load the options
data = load_data()
monitor = pygame.display.Info()
current_screen = 'main_menu' if 'logged_in' in data else 'selection'
res = data['options']['res'] if data['options']['res'] != None else (monitor.current_w, monitor.current_h)
fps = data['options']['fps']

screens = {
    'selection': SelectionMenu, 'signup': SignUpMenu, 'login': LoginMenu, 
    'main_menu': MainMenu, 'game': Game, 'options_menu': OptionsMenu, 'leaderboard': LeaderboardMenu, 'credits_menu': CreditsMenu
    }

running = True
window = create_window(res)

while running:
    screen = screens[current_screen](window, fps)
    current_screen = screen.run()
    window = screen.window
    fps = screen.fps
    if current_screen not in screens:
        break

pygame.quit()