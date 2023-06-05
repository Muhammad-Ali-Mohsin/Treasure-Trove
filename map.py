import pygame
from variables import CELL_SIZE, MAP_RESOLUTION, MAZE_RESOLUTION, SCREEN, GAME_RESOLUTION

class Map:
    def __init__(self):
        self.explored_cells = set()
        self.surface = pygame.Surface(MAP_RESOLUTION)
        self.map_cell_size = MAP_RESOLUTION[0] // MAZE_RESOLUTION[0]

    def update_map(self, maze, player_location):
        """
        Adds all the cells near the player to the map
        """
        cell = maze.get_cell(coord=player_location)
        neighbours = maze.get_neighbours(cell, with_diagonals=True)
        neighbours = filter(lambda neighbour: not maze.is_wall(cell=neighbour), neighbours)
        self.explored_cells.update(neighbours)

    def draw(self, player_pos):
        """
        This draws the map onto it's own surface and then blits that surface onto the screen based on the camera displacement
        """
        player_cell = (player_pos[0] // CELL_SIZE, player_pos[1] // CELL_SIZE)
        self.surface.fill((224, 211, 175))

        # Draws the explored part of the maze
        for cell in self.explored_cells:
            pygame.draw.rect(self.surface, (185, 149, 102), (cell[0] * self.map_cell_size, cell[1] * self.map_cell_size, self.map_cell_size, self.map_cell_size))

        pygame.draw.rect(self.surface, (255, 0, 0), (player_cell[0] * self.map_cell_size, player_cell[1] * self.map_cell_size, self.map_cell_size, self.map_cell_size))

        # Draws the map surface onto the screen
        SCREEN.blit(self.surface, ((GAME_RESOLUTION[0] // 2) - (MAP_RESOLUTION[0] // 2), (GAME_RESOLUTION[1] // 2) - (MAP_RESOLUTION[1] // 2)))
