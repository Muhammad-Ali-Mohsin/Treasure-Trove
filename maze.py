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
        self.surface.fill((110, 180, 50))
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
    
    def get_random_cell(self):
        cell = (random.randint(0, self.resolution[0] - 1), random.randint(0, self.resolution[0] - 1))
        while self.get_cell(x=cell[0], y=cell[1]) != 0:
            cell = (random.randint(0, self.resolution[0] - 1), random.randint(0, self.resolution[0] - 1))
        return cell

    def get_maze(self):
        """
        Returns the maze itself
        """
        return self._maze
            
    def __repr__(self):
        return "\n".join([str(row) for row in self._maze])
    

def generate_maze(x, y, tile_size):
    """
    Uses a Randomised depth first search algorithm to generate a maze
    """
    # Creates the maze class with a slightly smaller resolution so the border walls can be added afterwards
    maze = Maze(x=x-2, y=y-2, tile_size=tile_size)

    def get_neighbours(cell):
        """
        Returns the neighbours which are 2 steps in either direction as well as the cell 1 step in that direction
        This represents the neighbouring cell and the wall to get to that cell
        """
        neighbours = set()
        # Adds the neighbours which are to the right and left of the cell
        for i in [2, -2]:
            if cell[0] + i > -1 and cell[0] + i < maze.resolution[0]:
                neighbours.add(((cell[0] + i, cell[1]), (cell[0] + (i // 2), cell[1])))

        # Adds the neighbours which are to the bottom and top of the cell
        for i in [2, -2]:
            if cell[1] + i > -1 and cell[1] + i < maze.resolution[1]:
                neighbours.add(((cell[0], cell[1] + i), (cell[0], cell[1] + (i // 2))))

        return neighbours

    # Picks a random starting cell and adds it to the stack
    starting_cell = (random.randint(0, maze.resolution[0] - 1), random.randint(0, maze.resolution[1] - 1))
    maze_stack = [starting_cell]

    # Keeps looping as long as there are cells in the stack
    while len(maze_stack) != 0:

        # Pops a cell off the stack
        current_cell = maze_stack.pop()

        # Gets the neighbours of the current cell and filters out and cells which have been cleared out 
        neighbours = list(get_neighbours(current_cell))
        neighbours = list(filter(lambda neighbour: maze.get_cell(neighbour[0][0], neighbour[0][1]) != 0, neighbours))

        if len(neighbours) != 0:
            # Adds the current cell back to the stack so it can be backtracked along
            maze_stack.append(current_cell)
            # Picks a random neighbour to move along
            neighbour = random.choice(neighbours)
            # Clears out the neighbour as well as the cell required to get there
            maze.change_cell(x=neighbour[0][0], y=neighbour[0][1], data=0)
            maze.change_cell(x=neighbour[1][0], y=neighbour[1][1], data=0)
            # Adds the neighbour to the stack
            maze_stack.append(neighbour[0])

    # Adds borders to the sides of the maze
    for i in range(maze.resolution[1]):
        maze._maze[i].insert(0, 1)
        maze._maze[i].append(1)
    
    # Adds borders to the top and bottom of the maze
    maze._maze.insert(0, [1 for i in range(x)])
    maze._maze.append([1 for i in range(x)])
    
    maze.resolution = (x, y)
    return maze
