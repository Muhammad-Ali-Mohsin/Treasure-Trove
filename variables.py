import pygame

clock = pygame.time.Clock()

# Constants
MAZE_RESOLUTION = (30, 30)
TILE_SIZE = 32
PLAYER_SIZE = 16
PLAYER_SPEED = 100

# Variables about the display
monitor = pygame.display.Info()
USER_RESOLUTION = [monitor.current_w, monitor.current_h]
#USER_RESOLUTION = [1000, 1000]
RESOLUTION = [645, 360]
WINDOW = pygame.display.set_mode(USER_RESOLUTION)
SCREEN = pygame.Surface(RESOLUTION)
COMPASS_SCALE = 2

# Image Loading
COMPASS_BASE_IMG = pygame.image.load("assets/images/compass_base_img.png").convert_alpha()
COMPASS_SPINNER_IMG = pygame.image.load("assets/images/compass_spinner_img.png").convert_alpha()
ICON_IMG = pygame.image.load("assets/images/icon.png").convert_alpha()

# Image Rescaling
COMPASS_BASE_IMG = pygame.transform.scale(COMPASS_BASE_IMG, (COMPASS_SCALE * COMPASS_BASE_IMG.get_width(), COMPASS_SCALE * COMPASS_BASE_IMG.get_width()))
COMPASS_SPINNER_IMG = pygame.transform.scale(COMPASS_SPINNER_IMG, (COMPASS_SCALE * COMPASS_SPINNER_IMG.get_width(), COMPASS_SCALE * COMPASS_SPINNER_IMG.get_width()))
