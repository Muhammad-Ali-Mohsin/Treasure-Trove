import pygame
from variables import TILE_SIZE

class Map:
    def __init__(self, resolution, maze_resolution):
        self.resolution = (resolution)
        self.explored_tiles = set()
        self.surface = pygame.Surface(resolution)
        self.map_tile_size = self.resolution[0] // maze_resolution[0]

    def update_map(self, maze, player_location):
        """
        Adds all the tiles near the player to the map
        """
        cell = maze.get_cell(coord=player_location)
        neighbours = maze.get_neighbours(cell, with_diagonals=True)
        neighbours_with_data = map(lambda neighbour: (neighbour, maze.is_wall(cell=neighbour)), neighbours)
        self.explored_tiles.update(neighbours_with_data)

    def draw(self, surface, pos, player_pos):
        """
        This draws the map onto it's own surface and then blits that surface onto the screen based on the camera displacement
        """
        cell = (player_pos[0] // TILE_SIZE, player_pos[1] // TILE_SIZE)
        self.surface.fill((224, 211, 175))

        # Draws the explored part of the maze
        for tile in self.explored_tiles:
            if tile[1] == False:
                pygame.draw.rect(self.surface, (185, 149, 102), (tile[0][0] * self.map_tile_size, tile[0][1] * self.map_tile_size, self.map_tile_size, self.map_tile_size))

        pygame.draw.rect(self.surface, (255, 0, 0), (cell[0] * self.map_tile_size, cell[1] * self.map_tile_size, self.map_tile_size, self.map_tile_size))

        # Draws the map surface onto the screen
        surface.blit(self.surface, (pos))
