# USAGE: maze = Maze(x, y)
import random
import pygame
from variables import MAZE_RESOLUTION, CELL_SIZE, CELL_CENTER_SIZE, REMOVED_CELLS, MAZE_SURFACE_RESOLUTION, MAZE_SURFACE

class Maze:
    def __init__(self, x, y):
        self.resolution = (x, y)
        self.surface = pygame.Surface(((x + 2) * CELL_SIZE, (y + 2) * CELL_SIZE))
        self.hedge_images = []
        self.path_images = []

        # Loads each hedge image and path image and adds it to their respective lists
        for i in range(16):
            img = pygame.image.load(f"assets/images/hedges/hedge_{i}.png").convert_alpha()
            self.hedge_images.append(img)
            img = pygame.image.load(f"assets/images/paths/path_{i}.png").convert_alpha()
            self.path_images.append(img)

        self._maze = [[len(self.path_images) for i in range(x)] for i in range(y)]

    def __repr__(self):
        return "\n".join([str(row) for row in self._maze])

    def get_cell_value(self, cell):
        """
        Returns the value of the given cell
        """
        return self._maze[cell[1]][cell[0]]
    
    def get_cell(self, coord):
        """
        Returns the given cell at a set of coords
        """
        return (coord[0] // CELL_SIZE, coord[1] // CELL_SIZE)
    
    
    def get_maze(self):
        """
        Returns the maze itself
        """
        return self._maze
    
    def get_random_cell(self):
        """
        Returns a random empty cell
        """
        cell = (random.randint(0, self.resolution[0] - 1), random.randint(0, self.resolution[0] - 1))
        while self.is_wall(cell=cell):
            cell = (random.randint(0, self.resolution[0] - 1), random.randint(0, self.resolution[0] - 1))
        return cell
    
    def get_neighbours(self, cell, with_diagonals=False):
        """
        Returns the neighbours for the cell
        """
        neighbours = []
        # Adds the neighbours which are to the right and left of the cell
        for i in [1, -1]:
            if cell[0] + i > -1 and cell[0] + i < self.resolution[0]:
                neighbours.append((cell[0] + i, cell[1]))

        # Adds the neighbours which are to the bottom and top of the cell
        for i in [1, -1]:
            if cell[1] + i > -1 and cell[1] + i < self.resolution[1]:
                neighbours.append((cell[0], cell[1] + i))

        if with_diagonals:
            # Adds the neighbours which diagonal to the cell
            for i in [1, -1]:
                for j in [1, -1]:
                    if (cell[0] + i > -1 and cell[0] + i < self.resolution[0]) and (cell[1] + j > -1 and cell[1] + j < self.resolution[1]):
                        neighbours.append((cell[0] + i, cell[1] + j))

        return neighbours
    
    def get_wall_neighbours_list(self, cell):
        """
        Returns a list of the sides of a cell which have walls
        """
        sides = []
        neighbours = self.get_neighbours(cell=cell)

        # Checks each of the neighbours to see whether they are a wall and what side they are one
        for neighbour in neighbours:
            if self.is_wall(neighbour):
                if neighbour[0] > cell[0]:
                    sides.append('right')
                elif neighbour[0] < cell[0]:
                    sides.append('left')
                elif neighbour[1] > cell[1]:
                    sides.append('bottom')
                else:
                    sides.append('top')

        return sides
    
    def get_cell_center(self, cell):
        """
        Returns the coordinates of the centre of a cell and a rect around the centre
        """
        cell_center = ((cell[0] * CELL_SIZE) + (CELL_SIZE // 2), (cell[1] * CELL_SIZE) + (CELL_SIZE // 2))
        rect = pygame.Rect(0, 0, CELL_CENTER_SIZE, CELL_CENTER_SIZE)
        rect.center = cell_center
        return cell_center, rect
    
    def get_cells_on_screen(self, player_pos):
        """
        Returns all the cells around the player which appear on the screen
        """
        # Checks how many cells can fit across the width and height of the maze surface
        x_length = (MAZE_SURFACE_RESOLUTION[0] // CELL_SIZE) + 2
        y_length = (MAZE_SURFACE_RESOLUTION[1] // CELL_SIZE) + 2
        # Gets the player's cell and calculates the first cell which appears on the screen
        player_cell = self.get_cell(player_pos)
        starting_cell = (player_cell[0] - (x_length // 2), player_cell[1] - (y_length // 2))
        # Loops through every cell which appears on the screen and adds it to the list if it is not past the maze resolution
        cells = []
        for y in range(y_length):
            for x in range(x_length):
                cell = (starting_cell[0] + x, starting_cell[1] + y)
                if not (cell[0] > MAZE_RESOLUTION[0] - 1 or cell[1] > MAZE_RESOLUTION[1] - 1):
                    cells.append((starting_cell[0] + x, starting_cell[1] + y))

        return cells
    
    def change_cell(self, cell, data):
        """
        Changes the given cell to a new value
        """
        self._maze[cell[1]][cell[0]] = data

    def is_wall(self, cell):
        """
        Returns whether a wall is present at the given cell or not
        """
        return self.get_cell_value(cell=cell) >= len(self.path_images)

    def draw(self, camera_displacement, player_pos):
        """
        This draws the maze onto it's own surface and then blits that surface onto the screen based on the camera displacement
        """
        self.surface.fill((35, 72, 39))

        # Gets the cells near the player that should appear on the screen
        cells = self.get_cells_on_screen(player_pos=player_pos)
        # Draws each cell
        for x, y in cells:
            if self.is_wall(cell=(x, y)):
                hedge_image = self.hedge_images[self.get_cell_value(cell=(x, y)) - len(self.path_images)]
                self.surface.blit(hedge_image, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            else:
                path_image = self.path_images[self.get_cell_value(cell=(x, y))]
                self.surface.blit(path_image, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Draws the maze surface onto the screen based on the camera displacement
        MAZE_SURFACE.blit(self.surface, (-camera_displacement[0], -camera_displacement[1]))
    

def generate_maze():
    """
    Uses a Randomised depth first search algorithm to generate a maze
    """
    # Creates the maze class with a slightly smaller resolution so the border walls can be added afterwards
    maze = Maze(x=MAZE_RESOLUTION[0] - 2, y=MAZE_RESOLUTION[1] - 2)

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

        # Gets the neighbours of the current cell and filters out any cells which have been cleared out 
        neighbours = list(get_neighbours(current_cell))
        neighbours = list(filter(lambda neighbour: maze.is_wall(cell=neighbour[0]), neighbours))

        if len(neighbours) != 0:
            # Adds the current cell back to the stack so it can be backtracked along
            maze_stack.append(current_cell)
            # Picks a random neighbour to move along
            neighbour = random.choice(neighbours)
            # Clears out the neighbour as well as the cell required to get there
            maze.change_cell(cell=neighbour[0], data=0)
            maze.change_cell(cell=neighbour[1], data=0)
            # Adds the neighbour to the stack
            maze_stack.append(neighbour[0])

    # This removes a bunch of walls to make the maze more open and have more paths through it
    for i in range(REMOVED_CELLS):
        # This finds a random cell and checks whether it has 2 walls on opposite sides as those are the only type of walls that should be removed
        cell = (random.randint(0, maze.resolution[0] - 1), random.randint(0, maze.resolution[0] - 1))
        while not maze.is_wall(cell=cell) or maze.get_wall_neighbours_list(cell=cell) not in [['bottom', 'top'], ['right', 'left']]:
            cell = (random.randint(0, maze.resolution[0] - 1), random.randint(0, maze.resolution[0] - 1))
        maze.change_cell(cell=cell, data=0)

    # Adds borders to the sides of the maze
    for i in range(maze.resolution[1]):
        maze._maze[i].insert(0, len(maze.path_images))
        maze._maze[i].append(len(maze.path_images))
    
    # Adds borders to the top and bottom of the maze
    maze._maze.insert(0, [len(maze.path_images) for i in range(MAZE_RESOLUTION[0])])
    maze._maze.append([len(maze.path_images) for i in range(MAZE_RESOLUTION[0])])
    
    maze.resolution = MAZE_RESOLUTION

    # Changes each value in the maze based on the surrounding cells
    # This is a list of the possible combinations that can be had with surrounding walls
    combinations = (
        ['right', 'left', 'bottom', 'top'],
        ['right', 'left', 'bottom'],
        ['left', 'bottom', 'top'],
        ['right', 'left', 'top'],
        ['right', 'bottom', 'top'],
        ['bottom', 'top'],
        ['right', 'left'],
        ['top'],
        ['right'],
        ['bottom'],
        ['left'],
        ['right', 'top'],
        ['left', 'top'],
        ['right', 'bottom'],
        ['left', 'bottom'],
        []
    )
    for x in range(MAZE_RESOLUTION[0]):
        for y in range(MAZE_RESOLUTION[1]):
            # Changes the value of the maze (0 to 15 for paths and 16 to 31 for hedges)
            wall_neighbours_list = maze.get_wall_neighbours_list(cell=(x, y))
            value = combinations.index(wall_neighbours_list) + (len(maze.path_images) if maze.is_wall((x, y)) else 0)
            maze.change_cell(cell=(x, y), data=value)

    return maze
