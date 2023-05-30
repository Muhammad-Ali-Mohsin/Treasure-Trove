import pygame
from animation import Animation
from misc import Node, QueueFrontier

class Entity:
    def __init__(self, x, y, size, speed):
        self.rect = pygame.Rect(x, y, size, size)
        self.rect.center = (x, y)
        self.speed = speed

    def move(self, movement, maze, tile_size, dt):
        """
        Moves the entity based on the movement list
        Returns True or False based on whether the entity has collided
        """
        
        self.change_entity_animation(movement=movement)

        collision = False
        move_x = move_y = 0
        if movement['left']:
            move_x -= round(self.speed * dt)
        if movement['right']:
            move_x += round(self.speed * dt)
        if movement['up']:
            move_y -= round(self.speed * dt)
        if movement['down']:
            move_y += round(self.speed * dt)

        # This is the cell in the maze where the entity currently is
        cell = (self.rect.centerx // tile_size, self.rect.centery // tile_size)
        
        # Gets the neighbouring cells of the cell the entity is in
        neighbours = maze.get_neighbours(cell, with_diagonals=True)

        self.rect.x += move_x
        for neighbour in neighbours:
            # Checks whether the neighbouring cell is filled
            if maze.get_cell(neighbour[0], neighbour[1]) == 1:
                # Creates a rect for the neighbouring tile
                neighbour_rect = pygame.Rect(neighbour[0] * tile_size, neighbour[1] * tile_size, tile_size, tile_size)
                # Checks whether the rects are colliding with one another
                if self.rect.colliderect(neighbour_rect):
                    collision = True
                    # This means that the neighbour must have been on the right
                    if move_x > 0:
                        self.rect.right = neighbour_rect.left
                    # This means that the neighbour must have been on the left
                    if move_x < 0:
                        self.rect.left = neighbour_rect.right

        self.rect.y += move_y
        for neighbour in neighbours:
            # Checks whether the neighbouring cell is filled
            if maze.get_cell(neighbour[0], neighbour[1]) == 1:
                # Creates a rect for the neighbouring tile
                neighbour_rect = pygame.Rect(neighbour[0] * tile_size, neighbour[1] * tile_size, tile_size, tile_size)
                # Checks whether the rects are colliding with one another
                if self.rect.colliderect(neighbour_rect):
                    collision = True
                    # This means that the neighbour must have been on the bottom
                    if move_y > 0:
                        self.rect.bottom = neighbour_rect.top
                    # This means that the neighbour must have been on the top
                    if move_y < 0:
                        self.rect.top = neighbour_rect.bottom

        return collision
        
    def draw(self, screen, camera_displacement):
        """
        Draws the entity onto the screen
        """
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x - camera_displacement[0], self.rect.y - camera_displacement[1], self.rect.width, self.rect.height))
        
    def __repr__(self):
        return f"Entity(Location: {self.rect.center} )"
    

class Player(Entity):
    def __init__(self, x, y, size, speed, animations_path):
        super().__init__(x, y, size, speed)
        # Loads the animations
        self.animation = Animation()
        self.animation.load_animations(animations_path)

    def dig(self, treasure, tile_size):
        """
        Checks whether there is treasure at the current location
        """
        cell = (self.rect.centerx // tile_size, self.rect.centery // tile_size)
        if cell == treasure['cell']:
            success = True
        else:
            success = False

        return success
    
    def change_entity_animation(self, movement):
        """
        Changes the entity's animation based on their movements
        """
        if movement['left']:
            self.animation.change_animation(animation="running_sideways") if self.animation.current_animation != "running_sideways" else None
            self.animation.flipped = True
        elif movement['right']:
            self.animation.change_animation(animation="running_sideways") if self.animation.current_animation != "running_sideways" else None
            self.animation.flipped = False
        elif movement['up'] and self.animation.current_animation != "running_backwards":
            self.animation.change_animation(animation="running_backwards")
        elif movement['down'] and self.animation.current_animation != "running_forwards":
            self.animation.change_animation(animation="running_forwards")
        elif not movement['left'] and not movement['right'] and not movement['up'] and not movement['down'] and ("idle" not in self.animation.current_animation):
            if self.animation.current_animation == "running_sideways":
                self.animation.change_animation(animation="idle_sideways")
            elif self.animation.current_animation == "running_backwards":
                self.animation.change_animation(animation="idle_backwards")
            else:
                self.animation.change_animation(animation="idle_forwards")
    
    def draw(self, screen, camera_displacement):
        """
        Draws the player onto the screen
        """
        screen.blit(self.img, (self.rect.x - camera_displacement[0] - (self.img.get_width() // 2), self.rect.y - camera_displacement[1] - (self.img.get_height() // 2)))
        
class Enemy(Entity):
    def __init__(self, x, y, size, speed, animations_path, tile_center_size, refresh_interval):
        super().__init__(x, y, size, speed)
        # Loads the animations
        self.animation = Animation()
        self.animation.load_animations(animations_path)
        self.path = []
        self.tile_center_size = tile_center_size
        self.path_refresh_timer = 0
        self.path_refresh_interval = refresh_interval
    
    def draw(self, screen, camera_displacement):
        """
        Draws the Enemy onto the screen
        """
        screen.blit(self.img, (self.rect.x - camera_displacement[0] - (self.img.get_width() // 2), self.rect.y - camera_displacement[1] - (self.img.get_height() // 2)))

    def calculate_path(self, tile_size, player_location, maze):
        """
        Uses a Breadth First Search to find the shortest path from the enemy to the player
        """
        # Finds the cell the enemy is in and the destination cell which the player is in
        starting_cell = (self.rect.centerx // tile_size, self.rect.centery // tile_size)
        destination = (player_location[0] // tile_size, player_location[1] // tile_size)

        # Initialise frontier to starting position
        frontier = QueueFrontier()
        explored_cells = set()
        source_node = Node(starting_cell, None)
        frontier.add(source_node)

        while True:
            # Checks if the frontier is empty as if frontier is empty and target has not been found, there must be no possible path
            if frontier.empty():
                raise Exception("No path from enemy to player")
            
            # Removes the node from the front of the frontier
            node = frontier.remove()
            explored_cells.add(node.cell)

            # Checks whether the node is the target node
            if node.cell == destination:
                break
            else:
                # Adds the node's neighbours to the frontier if the cell in the maze in empty and they haven't been explored
                for neighbour in maze.get_neighbours(node.cell):
                    if maze.get_cell(neighbour[0], neighbour[1]) == 0 and neighbour not in explored_cells and not frontier.contains_cell(neighbour):
                        frontier.add(Node(neighbour, node))

        # Backtracks using the parent of each node to find the shortest path
        shortest_path = []
        while node.parent != None:
            shortest_path.insert(0, node.cell)
            node = node.parent

        self.path = shortest_path

    def get_cell_center(self, cell, tile_size):
        """
        Returns the coordinates of the centre of a cell and a rect around the centre
        """
        cell_center = ((cell[0] * tile_size) + (tile_size // 2), (cell[1] * tile_size) + (tile_size // 2))
        rect = pygame.Rect(0, 0, self.tile_center_size, self.tile_center_size)
        rect.center = cell_center
        return cell_center, rect
    
    def change_entity_animation(self, movement):
        """
        Changes the entity's animation based on their movements
        """
        if movement['left']:
            self.animation.change_animation(animation="running") if self.animation.current_animation != "running" else None
            self.animation.flipped = True
        elif movement['right']:
            self.animation.change_animation(animation="running") if self.animation.current_animation != "running" else None
            self.animation.flipped = False
        elif (movement['up'] or movement['down']) and self.animation.current_animation != "running":
            self.animation.change_animation(animation="running")
        elif not movement['left'] and not movement['right'] and not movement['up'] and not movement['down'] and self.animation.current_animation != "idle":
            self.animation.change_animation(animation="idle")
    
    def move_to_player(self, maze, tile_size, dt, player_location):
        """
        Refreshes the enemy's path based on the refresh timer and moves the enemy to the player
        """
        # Checks whether it's time to refresh the enemy's path and if not, increments the timer
        if self.path_refresh_timer >= self.path_refresh_interval:
            # Finds the rect of the cell the enemy is in and makes sure the enemy is fully within the cell before calculating new path
            enemy_cell = (self.rect.centerx // tile_size, self.rect.centery // tile_size)
            enemy_cell_rect = pygame.Rect(enemy_cell[0] * tile_size, enemy_cell[1] * tile_size, tile_size, tile_size)
            if enemy_cell_rect.contains(self.rect):
                # Calculates new path and resets the timer
                self.calculate_path(tile_size=tile_size, player_location=player_location, maze=maze)
                self.path_refresh_timer = 0
        else:
            self.path_refresh_timer += dt

        if len(self.path) != 0:
            # Gets the center of the cell which is the first in the enemy's path and a rect around that center
            cell_center, center_rect = self.get_cell_center(cell=self.path[0], tile_size=tile_size)

            # Checks whether the enemy rect is entirely within the center rect meaning the player must be in the center of the rect so it can be removed from the path
            if center_rect.contains(self.rect): self.path.remove(self.path[0])

            if len(self.path) != 0: cell_center, center_rect = self.get_cell_center(cell=self.path[0], tile_size=tile_size)

        else:
            cell_center = self.rect.center
        
        # Checks where the enemy needs to move based on the position of the enemy and the first cell in their path
        movement = {'left': False, 'right': False, 'up': False, 'down': False}
        if self.rect.centerx > cell_center[0]:
            movement['left'] = True
        elif self.rect.centerx < cell_center[0]:
            movement['right'] = True
        elif self.rect.centery < cell_center[1]:
            movement['down'] = True
        elif self.rect.centery > cell_center[1]:
            movement['up'] = True
        
        # Moves the player based on their movement
        self.move(movement=movement, maze=maze, tile_size=tile_size, dt=dt)



    
    
