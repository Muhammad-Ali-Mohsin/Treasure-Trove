import pygame
from variables import CELL_SIZE, MAP_RESOLUTION, MAZE_RESOLUTION, SCREEN, GAME_RESOLUTION, PLAYER_ICON_IMG, ENEMY_ICON_IMG, MAP_BACKGROUND_IMG

class Map:
    def __init__(self):
        self.explored_cells = set()
        self.surface = pygame.Surface(MAP_RESOLUTION, pygame.SRCALPHA)
        self.map_cell_size = MAP_RESOLUTION[0] // MAZE_RESOLUTION[0]

    def update_map(self, maze, player_location):
        """
        Adds all the cells near the player to the map
        """
        cell = maze.get_cell(coord=player_location)
        neighbours = maze.get_neighbours(cell, with_diagonals=True)
        neighbours = filter(lambda neighbour: not maze.is_wall(cell=neighbour), neighbours)
        self.explored_cells.update(neighbours)

    def draw(self, player_pos, enemies):
        """
        This draws the map onto it's own surface and then blits that surface onto the screen based on the camera displacement
        """
        self.surface.fill((0, 0, 0, 0))

        # Draws the explored part of the maze
        for cell in self.explored_cells:
            pygame.draw.rect(self.surface, (185, 149, 102), (cell[0] * self.map_cell_size, cell[1] * self.map_cell_size, self.map_cell_size, self.map_cell_size))

        # Draws the enemies
        for enemy in enemies:
            enemy_cell = (enemy.rect.centerx // CELL_SIZE, enemy.rect.centery // CELL_SIZE)
            pos = ((enemy_cell[0] * self.map_cell_size) + (self.map_cell_size // 2) - (ENEMY_ICON_IMG.get_width() // 2), (enemy_cell[1] * self.map_cell_size) + (self.map_cell_size // 2) - (ENEMY_ICON_IMG.get_height() // 2))
            self.surface.blit(ENEMY_ICON_IMG, pos)
           
        # Draws the player
        player_cell = (player_pos[0] // CELL_SIZE, player_pos[1] // CELL_SIZE)
        pos = ((player_cell[0] * self.map_cell_size) + (self.map_cell_size // 2) - (PLAYER_ICON_IMG.get_width() // 2), (player_cell[1] * self.map_cell_size) + (self.map_cell_size // 2) - (PLAYER_ICON_IMG.get_height() // 2))
        self.surface.blit(PLAYER_ICON_IMG, pos)
       
        # Draws the map surface onto the screen
        SCREEN.blit(MAP_BACKGROUND_IMG, ((GAME_RESOLUTION[0] // 2) - (MAP_RESOLUTION[0] // 2) - 100, (GAME_RESOLUTION[1] // 2) - (MAP_RESOLUTION[1] // 2) - 100))
        SCREEN.blit(self.surface, ((GAME_RESOLUTION[0] // 2) - (MAP_RESOLUTION[0] // 2), (GAME_RESOLUTION[1] // 2) - (MAP_RESOLUTION[1] // 2)))
