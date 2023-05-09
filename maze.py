# USAGE: maze = Maze(x, y)
import random
import pygame

class Maze:
    def __init__(self, x, y, tile_size):
        self.resolution = (x, y)
        self._maze = [[1 for i in range(x)] for i in range(y)]
        self.surface = pygame.Surface(((x + 2) * tile_size, (y + 2) * tile_size))
        self.tile_size = tile_size

    def draw(self, surface, camera_displacement):
        """
        This draws the maze onto it's own surface and then blits that surface onto the screen based on the camera displacement
        """
        self.surface.fill((255, 255, 255))
        # Draws the maze
        for y in range(self.resolution[1]):
            for x in range(self.resolution[0]):
                if self.get_cell(x, y) == 1:
                    pygame.draw.rect(self.surface, (0, 0, 0), (x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size))

        # Draws the maze surface onto the screen based on the camera displacement
        surface.blit(self.surface, (-camera_displacement[0], -camera_displacement[1]))

    def change_cell(self, x, y, data):
        """
        Changes the cell at (x, y) to the value of data
        """
        self._maze[y][x] = data

    def get_cell(self, x, y):
        """
        Returns the cell at (x, y)
        """
        return self._maze[y][x]

    def get_neighbours(self, cell, with_diagonals=False):
        """
        Returns the neighbours for the cell
        """
        neighbours = set()
        # Adds the neighbours which are to the right and left of the cell
        for i in [1, -1]:
            if cell[0] + i > -1 and cell[0] + i < self.resolution[0]:
                neighbours.add((cell[0] + i, cell[1]))

        # Adds the neighbours which are to the bottom and top of the cell
        for i in [1, -1]:
            if cell[1] + i > -1 and cell[1] + i < self.resolution[1]:
                neighbours.add((cell[0], cell[1] + i))

        if with_diagonals:
            # Adds the neighbours which diagonal to the cell
            for i in [1, -1]:
                for j in [1, -1]:
                    if (cell[0] + i > -1 and cell[0] + i < self.resolution[0]) and (cell[1] + j > -1 and cell[1] + j < self.resolution[1]):
                        neighbours.add((cell[0] + i, cell[1] + j))

        return neighbours

    def get_maze(self):
        """
        Returns the maze itself
        """
        return self._maze
            
    def __repr__(self):
        return "\n".join([str(row) for row in self._maze])
    

def generate_maze(x, y, tile_size):
    """
    Uses a modified version of Prim's algorithm to generate a maze
    """
    maze = Maze(x=x-2, y=y-2, tile_size=tile_size)
    # Random starting cell
    starting_cell = (random.randint(0, maze.resolution[0] - 1), random.randint(0, maze.resolution[1] - 1))
    # List of cells to be explored and list of the cells that have been explored
    cells_list = []
    explored_cells = set()
    explored_cells.add(starting_cell)
    # Empty the starting cell (0 represents empty cell)
    maze.change_cell(x=starting_cell[0], y=starting_cell[1], data=0)
    # Adds all the initial neighbours to the cells list
    neighbours = maze.get_neighbours(cell=starting_cell)
    for neighbour in neighbours: cells_list.append(neighbour)

    # Keeps running as long as there are cells to be explored
    while len(cells_list) != 0:
        # Picks a random cell from the list of cells to be explored
        current_cell = random.choice(cells_list)
        neighbours = maze.get_neighbours(cell=current_cell)
        # Checks how many of the lists neighbours have been explored
        explored_neighbours = 0
        for neighbour in neighbours:
            if neighbour in explored_cells:
                explored_neighbours += 1
        # If less than two neighbours have been explored, make the cell part of the maze and add the cell's neighbours to the cells to be explored
        if explored_neighbours < 2:
            maze.change_cell(x=current_cell[0], y=current_cell[1], data=0)
            for neighbour in neighbours: cells_list.append(neighbour)
        # Remove the cell from the list of cells to be explored as it has been explored
        cells_list.remove(current_cell)
        explored_cells.add(current_cell)

    for i in range(maze.resolution[1]):
        maze._maze[i].insert(0, 1)
        maze._maze[i].append(1)
    
    maze._maze.insert(0, [1 for i in range(x)])
    maze._maze.append([1 for i in range(x)])
    
    maze.resolution = (x, y)

    return maze
