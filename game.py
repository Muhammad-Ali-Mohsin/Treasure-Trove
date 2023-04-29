import pygame, sys, os, random
from time import time
from maze import Maze
from player import Player

#Constants
MAZE_RESOLUTION = (50, 50)
TILE_SIZE = 32
PLAYER_SIZE = 16

#Pygame stuff
pygame.init()
clock = pygame.time.Clock()

#Variables about the display
monitor = pygame.display.Info()
USER_RESOLUTION = [1000, 500]
RESOLUTION = [1000, 500]
WINDOW = pygame.display.set_mode(USER_RESOLUTION)
SCREEN = pygame.Surface(RESOLUTION)
pygame.mouse.set_visible(False)



class Game:
    def __init__(self):
        self.last_time = time()
        self.fps = 60
        self.maze = Maze(x=MAZE_RESOLUTION[0], y=MAZE_RESOLUTION[1])
        self.maze.generate_maze()
        self.scroll = [0, 0]
        self.player = Player(x=50, y=50, size=PLAYER_SIZE, speed=3)
        self.movement = {'left': False, 'right': False, 'up': False, 'down': False}

    def update_display(self):
        SCREEN.fill((255, 255, 255))

        # Draws the maze
        maze = self.maze.get_maze()
        for y in range(len(maze)):
            for x in range(len(maze)):
                if self.maze.get_cell(x, y) == 1:
                    pygame.draw.rect(SCREEN, (0, 0, 0), (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))






        cell = (self.player.rect.centerx // TILE_SIZE, self.player.rect.centery // TILE_SIZE)
        pygame.draw.rect(SCREEN, (0, 255, 0), (cell[0] * TILE_SIZE, cell[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        


        neighbours = self.maze.get_neighbours(cell)
        for neighbour in neighbours:
            if self.maze.get_cell(neighbour[0], neighbour[1]) == 1:
                neighbour_rect = pygame.Rect(neighbour[0] * TILE_SIZE, neighbour[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(SCREEN, (0, 0, 255), neighbour_rect)
                if self.player.rect.colliderect(neighbour_rect):
                    pygame.draw.rect(SCREEN, (255, 0, 255), neighbour_rect)
                    print(f"Display: {neighbour_rect.center}, {self.player.rect.center}")
                    exit(0)






        # Draws the player
        self.player.draw(SCREEN)
                    
        #Shows the FPS
        font = pygame.font.SysFont("Impact", 25)
        fps_text = font.render(f"FPS: {round(self.fps)}", 1, pygame.Color("blue"))
        SCREEN.blit(fps_text, (10, 10))
        

        #Ouputs the display in the user resolution
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
                if event.key == pygame.K_TAB: #Checks to see if the key being pressed is escape
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


    def game_loop(self):
        dt = (time() - self.last_time)
        self.last_time = time()


        self.player.move(movement=self.movement, maze=self.maze, tile_size=TILE_SIZE)
        

        self.handle_events()
        self.update_display()
        clock.tick(60)
        self.fps = clock.get_fps()


game = Game()

while True:
    game.game_loop()
