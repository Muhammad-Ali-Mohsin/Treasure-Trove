import pygame

clock = pygame.time.Clock()
monitor = pygame.display.Info()

DEBUG_MODE = False

# Constants
MAZE_RESOLUTION = (20, 20)
TILE_SIZE = 32

# PLAYER CONSTANTS
PLAYER_SIZE = 16
PLAYER_SPEED = 100

# ENEMY CONSTANTS
ENEMY_SIZE = 16
ENEMY_SPEED = 100
TILE_CENTER_SIZE = 16
ENEMY_REFRESH_INTERVAL = 1

# Display Constants
USER_RESOLUTION = (monitor.current_w, monitor.current_h)
SUPPORTED_RESOLUTIONS = ((3840, 2160), (2560, 1440), (1920, 1080), (1280, 720), (854, 480), (640, 360), (426, 240))
GAME_RESOLUTION = (1920, 1080)
MAZE_SURFACE_RESOLUTION = (645, 360)
COMPASS_SCALE = 5.5

# Variables about the display
WINDOW = pygame.display.set_mode(USER_RESOLUTION)
SCREEN = pygame.Surface(GAME_RESOLUTION)
MAZE_SURFACE = pygame.Surface(MAZE_SURFACE_RESOLUTION)

# Image Loading
COMPASS_BASE_IMG = pygame.image.load("assets/images/compass_base_img.png").convert_alpha()
COMPASS_SPINNER_IMG = pygame.image.load("assets/images/compass_spinner_img.png").convert_alpha()
ICON_IMG = pygame.image.load("assets/images/icon.png").convert_alpha()

# Image Rescaling
COMPASS_BASE_IMG = pygame.transform.scale(COMPASS_BASE_IMG, (COMPASS_SCALE * COMPASS_BASE_IMG.get_width(), COMPASS_SCALE * COMPASS_BASE_IMG.get_width()))
COMPASS_SPINNER_IMG = pygame.transform.scale(COMPASS_SPINNER_IMG, (COMPASS_SCALE * COMPASS_SPINNER_IMG.get_width(), COMPASS_SCALE * COMPASS_SPINNER_IMG.get_width()))
