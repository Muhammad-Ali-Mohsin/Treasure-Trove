import pygame
from animation import Animation
from variables import CELL_SIZE, ENEMY_REFRESH_INTERVAL, ATTACK_COOLDOWN, PLAYER_SIZE, PLAYER_SPEED, ENEMY_SIZE, ENEMY_SPEED, ENEMY_LIFESPAN

class Entity:
    def __init__(self, x, y, size, speed):
        self.rect = pygame.Rect(x, y, size, size)
        self.rect.center = (x, y)
        self.speed = speed
        self.movement = [0, 0]
        
    def __repr__(self):
        return f"Entity(Location: {self.rect.center} )"

    def move(self, maze):
        """
        Moves the entity based on the movement list
        Returns True or False based on whether the entity has collided
        """
        
        self.change_entity_animation(movement=self.movement)

        collision = False

        # This is the cell in the maze where the entity currently is
        cell = maze.get_cell(self.rect.center)
        
        # Gets the neighbouring cells of the cell the entity is in
        neighbours = maze.get_neighbours(cell, with_diagonals=True)

        self.rect.x += self.movement[0]
        for neighbour in neighbours:
            # Checks whether the neighbouring cell is filled
            if maze.is_wall(cell=neighbour):
                # Creates a rect for the neighbouring cell
                neighbour_rect = pygame.Rect(neighbour[0] * CELL_SIZE, neighbour[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                # Checks whether the rects are colliding with one another
                if self.rect.colliderect(neighbour_rect):
                    collision = True
                    # This means that the neighbour must have been on the right
                    if self.movement[0] > 0:
                        self.rect.right = neighbour_rect.left
                    # This means that the neighbour must have been on the left
                    if self.movement[0] < 0:
                        self.rect.left = neighbour_rect.right

        self.rect.y += self.movement[1]
        for neighbour in neighbours:
            # Checks whether the neighbouring cell is filled
            if maze.is_wall(cell=neighbour):
                # Creates a rect for the neighbouring cell
                neighbour_rect = pygame.Rect(neighbour[0] * CELL_SIZE, neighbour[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                # Checks whether the rects are colliding with one another
                if self.rect.colliderect(neighbour_rect):
                    collision = True
                    # This means that the neighbour must have been on the bottom
                    if self.movement[1] > 0:
                        self.rect.bottom = neighbour_rect.top
                    # This means that the neighbour must have been on the top
                    if self.movement[1] < 0:
                        self.rect.top = neighbour_rect.bottom

        self.movement = [0, 0]

        return collision
    

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_SIZE, PLAYER_SPEED)
        # Loads the animations
        self.animation = Animation()
        self.animation.load_animations(animations_path="assets/animations/player")
        self.attacking = False
        self.attack_timer = 0
    
    def change_entity_animation(self, movement):
        """
        Changes the entity's animation based on their movements
        """
        if self.attacking:
            animation_name = f"attack_{self.animation.current_animation.split('_')[1]}"
            if self.animation.current_animation != animation_name: self.animation.change_animation(animation=animation_name)
        elif movement[0] != 0: # This means they must be moving either left of right
            if self.animation.current_animation != "running_sideways": self.animation.change_animation(animation="running_sideways")
            self.animation.flipped = True if movement[0] < 0 else False
        elif movement[1] < 0 and self.animation.current_animation != "running_backwards": # This means they must be running up the screen
            self.animation.change_animation(animation="running_backwards")
        elif movement[1] > 0 and self.animation.current_animation != "running_forwards": # This means they must be running down the screen
            self.animation.change_animation(animation="running_forwards")
        elif movement == [0, 0] and "idle" not in self.animation.current_animation:
            if self.animation.current_animation == "running_sideways":
                self.animation.change_animation(animation="idle_sideways")
            elif self.animation.current_animation == "running_backwards":
                self.animation.change_animation(animation="idle_backwards")
            else:
                self.animation.change_animation(animation="idle_forwards")

    def attack(self):
        """
        This will start a player attack if the player is not currently attacking
        """
        if not self.attacking:
            self.attack_timer = 0
            self.attacking = True

    def update_attack(self, treasure_cell, dt):
        """
        This will update an ongoing attack by incrementing the timer, stopping the attack if the timer has completed
        """
        # Increments the attack timer
        self.attack_timer += dt
        success = False
        # Checks whether the attack is over and ends it if so
        if self.attack_timer >= ATTACK_COOLDOWN:
            self.attack_timer = 0
            self.attacking = False
        else:
            rect = pygame.Rect(treasure_cell[0] * CELL_SIZE, treasure_cell[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if self.rect.colliderect(rect): success = True
        
        return success


class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, ENEMY_SIZE, ENEMY_SPEED)
        # Loads the animations
        self.animation = Animation()
        self.animation.load_animations(animations_path="assets/animations/slime")
        self.animation.load_animation(animation_name="death", path="assets/animations/slime/death", times=[0.5, 0.1, 0.2, 0.2, 0.2, 0.2], looped=False)
        self.path = []
        self.path_refresh_timer = 0
        self.age = 0
        self.has_died = False

    def calculate_path(self, player_location, maze):
        """
        Uses a Breadth First Search to find the shortest path from the enemy to the player
        Each node is formatted as [cell, parent cell]
        """
        # Finds the cell the enemy is in and the destination cell which the player is in
        starting_cell = maze.get_cell(self.rect.center)
        destination = maze.get_cell(player_location)

        # Initialise cell list to starting position
        cell_list = [(starting_cell, None)]
        explored_cells = set()

        while True:
            # Checks if the cell list is empty as if the cell_list is empty and target has not been found, there must be no possible path
            if len(cell_list) == 0:
                raise Exception("No path from enemy to player")
            
            # Removes the node from the front of the cell list
            node = cell_list.pop(0)
            explored_cells.add(node[0])

            # Checks whether the node is the target node
            if node[0] == destination:
                break
            else:
                # Adds the node's neighbours to the cell list if the cell in the maze in empty and they haven't been explored
                for neighbour in maze.get_neighbours(cell=node[0]):
                    if not maze.is_wall(cell=neighbour) and neighbour not in explored_cells and not any(cell == node[0] for cell in cell_list):
                        cell_list.append((neighbour, node))

        # Backtracks using the parent of each node to find the shortest path
        shortest_path = []
        while node[1] != None:
            shortest_path.insert(0, node[0])
            node = node[1]

        self.path = shortest_path
    
    def change_entity_animation(self, movement):
        """
        Changes the entity's animation based on their movements
        """
        if movement[0] != 0:
            if self.animation.current_animation != "running": self.animation.change_animation(animation="running")
            self.animation.flipped = True if movement[0] < 0 else False
        elif movement[1] != 0 and self.animation.current_animation != "running":
            self.animation.change_animation(animation="running")
        elif movement == [0, 0] and self.animation.current_animation != "idle":
            self.animation.change_animation(animation="idle")
    
    def move_to_player(self, maze, dt, player_location):
        """
        Refreshes the enemy's path based on the refresh timer and moves the enemy to the player
        """
        # Adds the enemy's age and marks it as dead if it's past its lifetime and the death animation is over
        self.age += dt
        if self.age >= ENEMY_LIFESPAN:
            if self.animation.current_animation != "death": self.animation.change_animation(animation="death")
            if self.animation.frame == len(self.animation.animation_library[self.animation.current_animation]) - 1:
                self.has_died = True
            return
        # Checks whether it's time to refresh the enemy's path and if not, increments the timer
        if self.path_refresh_timer >= ENEMY_REFRESH_INTERVAL:
            # Finds the rect of the cell the enemy is in and makes sure the enemy is fully within the cell before calculating new path
            enemy_cell = maze.get_cell(self.rect.center)
            enemy_cell_rect = pygame.Rect(enemy_cell[0] * CELL_SIZE, enemy_cell[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if enemy_cell_rect.contains(self.rect):
                # Calculates new path and resets the timer
                self.calculate_path(player_location=player_location, maze=maze)
                self.path_refresh_timer = 0
        else:
            self.path_refresh_timer += dt

        if len(self.path) != 0:
            # Gets the center of the cell which is the first in the enemy's path and a rect around that center
            cell_center, center_rect = maze.get_cell_center(cell=self.path[0])

            # Checks whether the enemy rect is entirely within the center rect meaning the enemy must be in the center of the rect so it can be removed from the path
            if center_rect.contains(self.rect): self.path.remove(self.path[0])

            # Gets the new cell center if there are still more cells in the enemy's path
            if len(self.path) != 0: cell_center, center_rect = maze.get_cell_center(cell=self.path[0])

        else:
            cell_center = self.rect.center
        
        # Checks where the enemy needs to move based on the position of the enemy and the first cell in their path
        if self.rect.centerx > cell_center[0]:
            self.movement[0] -= round(self.speed * dt)
        elif self.rect.centerx < cell_center[0]:
            self.movement[0] += round(self.speed * dt)
        elif self.rect.centery < cell_center[1]:
            self.movement[1] += round(self.speed * dt)
        elif self.rect.centery > cell_center[1]:
            self.movement[1] -= round(self.speed * dt)
        
        # Moves the player based on their movement
        self.move(maze=maze)



    
    
