import random

import pygame

class Maze:
    def __init__(self, game, tile_size, resolution):
        self.game = game
        self.tile_size = tile_size
        self.tiles = {}
        self.resolution = resolution
        self.flowers = {}

    def get_loc(self, pos):
        """
        Gets the tile location of a given position
        """
        return (int(pos[0] / self.tile_size), int(pos[1] / self.tile_size))
    
    def get_tile(self, pos):
        """
        Gets the tile at a position
        """
        return self.tiles[self.get_loc(pos)]

    def get_neighbours(self, tile, diagonals=True):
        """
        Gets all the neighbouring tiles around a given tile
        """
        neighbours = []
        loc = tile['loc']

        # Gets the neighbours to the left and right
        for x in (1, -1):
            if (loc[0] + x, loc[1]) in self.tiles:
                neighbours.append(self.tiles[(loc[0] + x, loc[1])])
        
        # Gets the neighbours on the top and bottom
        for y in (1, -1):
            if (loc[0], loc[1] + y) in self.tiles:
                neighbours.append(self.tiles[(loc[0], loc[1] + y)])

        # Retrieves the diagonal neighbours
        if diagonals:
            for x in (1, -1):
                for y in (1, -1):
                    if (loc[0] + x, loc[1] + y) in self.tiles:
                        neighbours.append(self.tiles[(loc[0] + x, loc[1] + y)])

        return neighbours
    
    def get_neighbour_rects(self, tile, diagonals=True):
        """
        Returns rects for the hedge neighbours of a given tile
        """
        rects = []
        for neighbour in self.get_neighbours(tile, diagonals):
            if neighbour['type'] == "hedge":
                rects.append(pygame.Rect(neighbour['loc'][0] * self.tile_size, neighbour['loc'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects
    
    def get_hedge_sides(self, tile):
        """
        Returns a list of the sides of a given tile which are hedges
        """
        sides = []
        neighbours = self.get_neighbours(tile, diagonals=False)

        # Checks each of the neighbours to see whether they are a hedge and what side they are on
        for neighbour in neighbours:
            if neighbour['type'] == "hedge":
                if neighbour['loc'][0] > tile['loc'][0]:
                    sides.append("right")
                elif neighbour['loc'][0] < tile['loc'][0]:
                    sides.append("left")
                elif neighbour['loc'][1] > tile['loc'][1]:
                    sides.append("bottom")
                else:
                    sides.append("top")

        return sides
    
    def get_random_loc(self, type, border_limits=None, border_function='inside'):
        """
        Returns a random tile location of a specified type
        Allows you to optionally define two border locations for where the tile should fit between
        """
        # Sets default border limits to be the top left and bottom right of the screen
        if border_limits == None:
            border_limits = ((0, 0), self.resolution)

        # Generates a random location within the limits and keeps finding new locations until one is found which matches the type
        if border_function == 'inside':
            loc = (random.randint(border_limits[0][0], border_limits[1][0]), random.randint(border_limits[0][1], border_limits[1][1]))
            while self.tiles[loc]['type'] != type:
                loc = (random.randint(border_limits[0][0], border_limits[1][0]), random.randint(border_limits[0][1], border_limits[1][1]))

        # Generates a random location on te screen and keeps finding new locations until one is found which matches the type and is outside of the limits
        elif border_function == 'outside':
            loc = (random.randint(0, self.resolution[0] - 1), random.randint(0, self.resolution[0] - 1))
            while self.tiles[loc]['type'] != type or (loc[0] > border_limits[0][0] and loc[0] < border_limits[1][0] and loc[1] > border_limits[0][1] and loc[1] < border_limits[1][1]):
                loc = (random.randint(0, self.resolution[0] - 1), random.randint(0, self.resolution[0] - 1))

        return loc
                
    
    def draw(self):
        """
        Draws all the tiles visible on the screen
        """
        top_left_loc = self.get_loc(self.game.camera_displacement)
        for x in range(-1, self.game.display.get_width() // self.tile_size + 2):
            for y in range(-1, self.game.display.get_height() // self.tile_size + 2):
                loc = (top_left_loc[0] + x, top_left_loc[1] + y)

                # Checks if the tile exists and blits it to the screen if it does
                if loc in self.tiles:
                    tile = self.tiles[loc]
                    self.game.display.blit(self.game.images[tile['type']][tile['img_index']], (loc[0] * self.tile_size - self.game.camera_displacement[0], loc[1] * self.tile_size - self.game.camera_displacement[1]))
                
                # Checks if there's any flowers at that location and blits the flowers
                if loc in self.flowers:
                    for flower_index in self.flowers[loc]:
                        self.game.display.blit(self.game.images['flowers'][flower_index], (loc[0] * self.tile_size - self.game.camera_displacement[0], loc[1] * self.tile_size - self.game.camera_displacement[1]))



def generate_maze(game, tile_size, maze_resolution, removed_tiles):
    """
    Uses a Randomised depth first search algorithm to generate a maze
    """
    # Creates the maze object
    maze = Maze(game, tile_size, maze_resolution)

    # Fills in the maze with hedges
    for x in range(maze_resolution[0]):
        for y in range(maze_resolution[1]):
            maze.tiles[(x, y)] = {
                'loc': (x, y),
                'type': "hedge",
                'img_index': 0
            }

    # Picks a random starting tile and adds it to the stack
    starting_tile = maze.tiles[random.choice(list(maze.tiles))]
    maze_stack = [starting_tile]

    # Keeps looping as long as there are tiles in the stack
    while len(maze_stack) != 0:

        # Pops a tile off the stack
        current_tile = maze_stack.pop()
        neighbours = []
        loc = current_tile["loc"]

        # Adds the neighbours to the left and right of the tile
        for x in (2, -2):
            if (loc[0] + x, loc[1]) in maze.tiles and maze.tiles[(loc[0] + x, loc[1])]['type'] != "path":
                neighbours.append((maze.tiles[(loc[0] + x, loc[1])], maze.tiles[(loc[0] + (x / 2), loc[1])]))

        # Adds the neighbours to the top and bottom of the tile
        for y in (2, -2):
            if (loc[0], loc[1] + y) in maze.tiles and maze.tiles[(loc[0], loc[1] + y)]['type'] != "path":
                neighbours.append((maze.tiles[(loc[0], loc[1] + y)], maze.tiles[(loc[0], loc[1] + (y / 2))]))

        if len(neighbours) != 0:
            # Adds the current tile back to the stack so it can be backtracked along
            maze_stack.append(current_tile)
            # Picks a random neighbour to move along
            neighbour = random.choice(neighbours)
            # Turns the neighbour into a path as well as the tile required to get there
            neighbour[0]['type'] = "path"
            neighbour[1]['type']= "path"
            # Adds the neighbour to the stack
            maze_stack.append(neighbour[0])


    # This removes a bunch of hedges to make the maze more open and have more paths through it
    for i in range(removed_tiles):
        # This finds a random tile and checks whether it has 2 hedges on opposite sides as those are the only type of hedges that should be removed
        tile = maze.tiles[random.choice(list(maze.tiles))]
        while not tile['type'] == "hedge" or maze.get_hedge_sides(tile) not in [["bottom", "top"], ["right", "left"]]:
            tile = maze.tiles[random.choice(list(maze.tiles))]
        tile['type'] = "path"

    # This generates a bunch of flowers within the maze
    for i in range(200):
        # This finds a random tile which is a path
        tile = maze.tiles[random.choice(list(maze.tiles))]
        while not tile['type'] == "path":
            tile = maze.tiles[random.choice(list(maze.tiles))]

        # Checks whether the tile already has flowers and if it does, appends to the flowers list or creates a new flowers list if it doesn't
        if tile['loc'] in maze.flowers:
            maze.flowers[tile['loc']].append(random.randint(0, len(game.images['flowers']) - 1))
        else:
            maze.flowers[tile['loc']] = [random.randint(0, len(game.images['flowers']) - 1)]
            
    # Adds borders to the maze
    for y in range(maze_resolution[1]):
        for x in (-1, maze_resolution[0]):
            maze.tiles[(x, y)] = {'loc': (x, y), 'type': "hedge", 'img_index': 0}
    for x in range(maze_resolution[0] + 2):
        for y in (-1, maze_resolution[1]):
            maze.tiles[(x - 1, y)] = {'loc': (x - 1, y), 'type': "hedge", 'img_index': 0}

    # Changes the variant of the tile based on its surrounding tiles
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
    for loc in maze.tiles:
        tile = maze.tiles[loc]        
        hedge_sides = maze.get_hedge_sides(tile)
        tile['img_index'] = combinations.index(hedge_sides)

    return maze

