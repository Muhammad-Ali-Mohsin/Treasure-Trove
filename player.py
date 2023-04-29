import pygame

class Player:
    def __init__(self, x, y, size, speed):
        self.rect = pygame.Rect(x, y, size, size)
        self.rect.center = (x, y)
        self.speed = speed

        self.collision_counter = 0

    def move(self, movement, maze, tile_size):
        """
        Moves the player based on the movement list
        Returns True or False based on whether the player has collided
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
        
        self.rect.x += move_x
        self.rect.y += move_y

        # This is the cell in the maze where the player currently is
        cell = (self.rect.centerx // tile_size, self.rect.centery // tile_size)
        

        # Gets the neighbouring cells of the cell the player is in
        neighbours = maze.get_neighbours(cell)

        #print(cell, neighbours)

        for neighbour in neighbours:
            # Checks whether the neighbouring cell is filled
            if maze.get_cell(neighbour[0], neighbour[1]) == 1:
                # Creates a rect for the neighbouring tile
                neighbour_rect = pygame.Rect(neighbour[0] * tile_size, neighbour[1] * tile_size, tile_size, tile_size)
                print(f"Player: {neighbour_rect.center}, {self.rect.center}")
                # Checks whether the rects are colliding with one another
                if self.rect.colliderect(neighbour_rect):
                    print(f"Collision detected: {self.collision_counter}")
                    collision = True
                    self.collision_counter += 1
                    
                    # This means that the neighbour must have been on the right
                    if move_x > 0:
                        self.rect.right = neighbour_rect.left
                    # This means that the neighbour must have been on the left
                    if move_x < 0:
                        self.rect.left = neighbour_rect.right
                    # This means that the neighbour must have been on the bottom
                    if move_y > 0:
                        self.rect.bottom = neighbour_rect.top
                    # This means that the neighbour must have been on the top
                    if move_y < 0:
                        self.rect.top = neighbour_rect.bottom


            return collision
        

    def draw(self, screen):
        """
        Draws the player onto the screen
        """
        pygame.draw.rect(screen, (255, 0, 0), self.rect)
        

            
    def __repr__(self):
        return f"Player(Location: {self.rect.center} )"
