import pygame, sys, os, random
from time import time
from maze import generate_maze
from entities import Player
from compass import Compass

random.seed(10)

# Constants
MAZE_RESOLUTION = (31, 31)
TILE_SIZE = 32
PLAYER_SIZE = 16

# Pygame stuff
pygame.init()
clock = pygame.time.Clock()

# Variables about the display
monitor = pygame.display.Info()
USER_RESOLUTION = [monitor.current_w, monitor.current_h]
USER_RESOLUTION = [1000, 1000]
RESOLUTION = [1000, 1000]
WINDOW = pygame.display.set_mode(USER_RESOLUTION)
SCREEN = pygame.Surface(RESOLUTION)
#pygame.mouse.set_visible(False)
pygame.display.set_caption("Treasure Trove")
pygame.display.set_icon(pygame.image.load("assets/images/icon.png"))

#Image Loading
COMPASS_BASE_IMG = pygame.image.load("assets/images/compass_base_img.png").convert_alpha()
COMPASS_SPINNER_IMG = pygame.image.load("assets/images/compass_spinner_img.png").convert_alpha()

#Image Rescaling
COMPASS_BASE_IMG = pygame.transform.scale(COMPASS_BASE_IMG, (4 * COMPASS_BASE_IMG.get_width(), 4 * COMPASS_BASE_IMG.get_width()))
COMPASS_SPINNER_IMG = pygame.transform.scale(COMPASS_SPINNER_IMG, (4 * COMPASS_SPINNER_IMG.get_width(), 4 * COMPASS_SPINNER_IMG.get_width()))



class Game:
    def __init__(self):
        self.last_time = time()
        self.fps = 60
        self.maze = generate_maze(x=MAZE_RESOLUTION[0], y=MAZE_RESOLUTION[1], tile_size=TILE_SIZE)
        self.generate_treasure()
        self.gold = 0
        self.camera_displacement = [0, 0]

        cell = (random.randint(0, self.maze.resolution[0] - 1), random.randint(0, self.maze.resolution[0] - 1))
        while self.maze.get_cell(x=cell[0], y=cell[1]) != 0:
            cell = (random.randint(0, self.maze.resolution[0] - 1), random.randint(0, self.maze.resolution[0] - 1))
        
        self.player = Player(x=cell[0] * TILE_SIZE + (TILE_SIZE // 2), y=cell[1] * TILE_SIZE + (TILE_SIZE // 2), size=PLAYER_SIZE, speed=150)
        self.movement = {'left': False, 'right': False, 'up': False, 'down': False}
        self.compass = Compass(base_img=COMPASS_BASE_IMG, spinner_img=COMPASS_SPINNER_IMG)

    def update_display(self):
        """
        Updates the screen
        """
        SCREEN.fill((255, 255, 255))

        self.maze.draw(SCREEN, self.camera_displacement)

        # Draws the treasure
        pygame.draw.rect(SCREEN, (255, 255, 0), (self.treasure['cell'][0] * TILE_SIZE - self.camera_displacement[0], self.treasure['cell'][1] * TILE_SIZE - self.camera_displacement[1], TILE_SIZE, TILE_SIZE))


        # Draws the player
        self.player.draw(SCREEN, self.camera_displacement)
                    
        # Shows the FPS
        font = pygame.font.SysFont("Impact", 25)
        fps_text = font.render(f"FPS: {round(self.fps)}", 1, pygame.Color("blue"))
        SCREEN.blit(fps_text, (10, 10))
        
        #Draws the Compass
        self.compass.draw(surface=SCREEN, x=RESOLUTION[0] - COMPASS_BASE_IMG.get_width(), y=10)

        # Ouputs the display in the user resolution
        WINDOW.blit(pygame.transform.scale(SCREEN, USER_RESOLUTION), (0, 0))
        pygame.display.flip()

    def handle_events(self):
        """
        Handles all input events such as key presses
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_LEFT:
                    self.movement['left'] = True
                if event.key == pygame.K_RIGHT:
                    self.movement['right'] = True
                if event.key == pygame.K_DOWN:
                    self.movement['down'] = True
                if event.key == pygame.K_UP:
                    self.movement['up'] = True
                if event.key == pygame.K_e:
                    self.dig()
                if event.key == pygame.K_TAB:
                    self.paused = not self.paused

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.movement['left'] = False
                if event.key == pygame.K_RIGHT:
                    self.movement['right'] = False
                if event.key == pygame.K_DOWN:
                    self.movement['down'] = False
                if event.key == pygame.K_UP:
                    self.movement['up'] = False

    def generate_treasure(self):
        """
        Generates treasure on a random cell in the maze
        """
        cell = (random.randint(0, self.maze.resolution[0] - 1), random.randint(0, self.maze.resolution[0] - 1))
        while self.maze.get_cell(x=cell[0], y=cell[1]) != 0:
            cell = (random.randint(0, self.maze.resolution[0] - 1), random.randint(0, self.maze.resolution[0] - 1))
        self.treasure = {'cell': cell, 'dig_counter': 0}

    def dig(self):
        """
        Attempts to dig for treasure at the player's current cell
        """
        success = self.player.dig(treasure=self.treasure, tile_size=TILE_SIZE)
        if success:
            self.treasure['dig_counter'] += 1
            # If the player has dug 3 times to fully uncover the treasure
            if self.treasure['dig_counter'] == 3:
                # Generate new treausre
                self.generate_treasure()
                # Give the player 100 gold
                self.gold += 100
        else:
            pass


    def game_loop(self):
        """
        The game loop
        """
        dt = (time() - self.last_time)
        self.last_time = time()
        player_cell = (self.player.rect.centerx // TILE_SIZE, self.player.rect.centery // TILE_SIZE)

        self.camera_displacement[0] = self.player.rect.centerx - RESOLUTION[0] // 2
        self.camera_displacement[1] = self.player.rect.centery - RESOLUTION[1] // 2


        self.player.move(movement=self.movement, maze=self.maze, tile_size=TILE_SIZE, dt=dt)

        self.compass.calculate_angle(player_location=player_cell, treasure_location=self.treasure['cell'], dt=dt)
        

        self.handle_events()
        self.update_display()
        clock.tick()
        self.fps = clock.get_fps()


game = Game()

while True:
    game.game_loop()
