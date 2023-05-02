import pygame

class Entity:
    def __init__(self, x, y, size, speed):
        self.rect = pygame.Rect(x, y, size, size)
        self.rect.center = (x, y)
        self.speed = speed

    def move(self, movement, maze, tile_size):
        """
        Moves the entity based on the movement list
        Returns True or False based on whether the entity has collided
        """
        
        collision = False
        move_x = move_y = 0
        if movement['left']:
            move_x -= self.speed
        if movement['right']:
            move_x += self.speed
        if movement['up']:
            move_y -= self.speed
        if movement['down']:
            move_y += self.speed

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
        
    def draw(self, screen):
        """
        Draws the entity onto the screen
        """
        pygame.draw.rect(screen, (255, 0, 0), self.rect)
        
    def __repr__(self):
        return f"Entity(Location: {self.rect.center} )"
    

class Player(Entity):
    def __init__(self, x, y, size, speed):
        super().__init__(x, y, size, speed)
