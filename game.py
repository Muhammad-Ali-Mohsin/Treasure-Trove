import pygame, sys, os, random
from time import time
from maze import generate_maze
from entities import Player

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
pygame.mouse.set_visible(False)
pygame.display.set_caption("Treasure Trove")
pygame.display.set_icon(pygame.image.load("icon.png"))



class Game:
    def __init__(self):
        self.last_time = time()
        self.fps = 60
        self.maze = generate_maze(x=MAZE_RESOLUTION[0], y=MAZE_RESOLUTION[1])
        self.generate_treasure()
        self.gold = 0
        self.camera_displacement = [0, 0]

        cell = (random.randint(0, self.maze.resolution[0] - 1), random.randint(0, self.maze.resolution[0] - 1))
        while self.maze.get_cell(x=cell[0], y=cell[1]) != 0:
            cell = (random.randint(0, self.maze.resolution[0] - 1), random.randint(0, self.maze.resolution[0] - 1))
        
        self.player = Player(x=cell[0] * TILE_SIZE + (TILE_SIZE // 2), y=cell[1] * TILE_SIZE + (TILE_SIZE // 2), size=PLAYER_SIZE, speed=150)
        self.movement = {'left': False, 'right': False, 'up': False, 'down': False}

    def update_display(self):
        SCREEN.fill((255, 255, 255))

        # Draws the maze
        maze = self.maze.get_maze()
        for y in range(len(maze)):
            for x in range(len(maze)):
                if self.maze.get_cell(x, y) == 1:
                    pygame.draw.rect(SCREEN, (0, 0, 0), (x * TILE_SIZE - self.camera_displacement[0], y * TILE_SIZE - self.camera_displacement[1], TILE_SIZE, TILE_SIZE))

        # Draws the treasure
        pygame.draw.rect(SCREEN, (255, 255, 0), (self.treasure['cell'][0] * TILE_SIZE - self.camera_displacement[0], self.treasure['cell'][1] * TILE_SIZE - self.camera_displacement[1], TILE_SIZE, TILE_SIZE))

        # Draws the player
        self.player.draw(SCREEN, self.camera_displacement)
                    
        # Shows the FPS
        font = pygame.font.SysFont("Impact", 25)
        fps_text = font.render(f"FPS: {round(self.fps)}", 1, pygame.Color("blue"))
        SCREEN.blit(fps_text, (10, 10))
        

        # Ouputs the display in the user resolution
        WINDOW.blit(pygame.transform.scale(SCREEN, USER_RESOLUTION), (0, 0))
        pygame.display.update()

    def handle_events(self):
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
        cell = (random.randint(0, self.maze.resolution[0] - 1), random.randint(0, self.maze.resolution[0] - 1))
        while self.maze.get_cell(x=cell[0], y=cell[1]) != 0:
            cell = (random.randint(0, self.maze.resolution[0] - 1), random.randint(0, self.maze.resolution[0] - 1))
        self.treasure = {'cell': cell, 'dig_counter': 0}

    def dig(self):
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
        dt = (time() - self.last_time)
        self.last_time = time()

        self.camera_displacement[0] = self.player.rect.centerx - SCREEN.get_width() // 2
        self.camera_displacement[1] = self.player.rect.centery - SCREEN.get_height() // 2


        self.player.move(movement=self.movement, maze=self.maze, tile_size=TILE_SIZE, dt=dt)
        

        self.handle_events()
        self.update_display()
        clock.tick()
        self.fps = clock.get_fps()


game = Game()

while True:
    game.game_loop()
