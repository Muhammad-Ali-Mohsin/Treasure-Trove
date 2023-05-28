import pygame

clock = pygame.time.Clock()

# Constants
MAZE_RESOLUTION = (25, 25)
TILE_SIZE = 32
PRIMARY_COLOUR = (255, 202, 24)

# PLAYER CONSTANTS
PLAYER_SIZE = 16
PLAYER_SPEED = 100

# ENEMY CONSTANTS
ENEMY_SIZE = 16
ENEMY_SPEED = 120
TILE_CENTER_SIZE = 18
ENEMY_REFRESH_INTERVAL = 1

# Display Constants
SUPPORTED_RESOLUTIONS = ((3840, 2160), (2560, 1440), (1920, 1080), (1280, 720), (854, 480), (640, 360), (426, 240))
GAME_RESOLUTION = (1920, 1080)
MAZE_SURFACE_RESOLUTION = (426, 240)
COMPASS_SCALE = 5.5
CURSOR_SCALE = 3

# Variables about the display
SCREEN = pygame.Surface(GAME_RESOLUTION)
MAZE_SURFACE = pygame.Surface(MAZE_SURFACE_RESOLUTION)

# Image Loading
COMPASS_BASE_IMG = pygame.image.load("assets/images/compass_base_img.png").convert_alpha()
COMPASS_SPINNER_IMG = pygame.image.load("assets/images/compass_spinner_img.png").convert_alpha()
ICON_IMG = pygame.image.load("assets/images/icon.png").convert_alpha()
CURSOR_1 = pygame.image.load("./assets/images/cursor_1.png").convert_alpha()
CURSOR_2 = pygame.image.load("./assets/images/cursor_0.png").convert_alpha()
PAUSE_SCREEN_BOX_IMG = pygame.image.load("assets/images/box.png").convert_alpha()

# Image Rescaling
COMPASS_BASE_IMG = pygame.transform.scale(COMPASS_BASE_IMG, (COMPASS_SCALE * COMPASS_BASE_IMG.get_width(), COMPASS_SCALE * COMPASS_BASE_IMG.get_width()))
COMPASS_SPINNER_IMG = pygame.transform.scale(COMPASS_SPINNER_IMG, (COMPASS_SCALE * COMPASS_SPINNER_IMG.get_width(), COMPASS_SCALE * COMPASS_SPINNER_IMG.get_width()))
CURSOR_1 = pygame.transform.scale(CURSOR_1, (CURSOR_1.get_width() * CURSOR_SCALE, CURSOR_1.get_height() * CURSOR_SCALE))
CURSOR_2 = pygame.transform.scale(CURSOR_2, (CURSOR_2.get_width() * CURSOR_SCALE, CURSOR_2.get_height() * CURSOR_SCALE))



