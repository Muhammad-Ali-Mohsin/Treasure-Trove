import pygame
from animation import Animation

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
    
    def draw(self, screen, camera_displacement):
        """
        Draws the player onto the screen
        """
        screen.blit(self.img, (self.rect.x - camera_displacement[0] - (self.img.get_width() // 2), self.rect.y - camera_displacement[1] - (self.img.get_height() // 2)))
    
    
