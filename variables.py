import pygame

clock = pygame.time.Clock()

# Constants
MAZE_RESOLUTION = (30, 30)
TILE_SIZE = 32
PLAYER_SIZE = 16

# Variables about the display
monitor = pygame.display.Info()
USER_RESOLUTION = [monitor.current_w, monitor.current_h]
USER_RESOLUTION = [1000, 1000]
RESOLUTION = [1000, 1000]
WINDOW = pygame.display.set_mode(USER_RESOLUTION)
SCREEN = pygame.Surface(RESOLUTION)

# Image Loading
COMPASS_BASE_IMG = pygame.image.load("assets/images/compass_base_img.png").convert_alpha()
COMPASS_SPINNER_IMG = pygame.image.load("assets/images/compass_spinner_img.png").convert_alpha()
ICON_IMG = pygame.image.load("assets/images/icon.png").convert_alpha()

# Image Rescaling
COMPASS_BASE_IMG = pygame.transform.scale(COMPASS_BASE_IMG, (4 * COMPASS_BASE_IMG.get_width(), 4 * COMPASS_BASE_IMG.get_width()))
COMPASS_SPINNER_IMG = pygame.transform.scale(COMPASS_SPINNER_IMG, (4 * COMPASS_SPINNER_IMG.get_width(), 4 * COMPASS_SPINNER_IMG.get_width()))
