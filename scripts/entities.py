import random
import math

import pygame

from scripts.animations import AnimationHandler
from scripts.particles import ParticleHandler

# This is the maximum distance from the center of a tile that an enemy can be for it to be considered in the center of that tile
MAX_DISTANCE = 2
# This is how long an entity is knocked back for
KNOCKBACK_TIME = 1
# This is how long an enemy stays stunned for
STUN_TIME = 1
# This is the attack range of the player
PLAYER_ATTACK_RANGE = 8
# This is the attack range of the enemy
ENEMY_ATTACK_RANGE = 4

class Entity:
    def __init__(self, game, loc, size, speed, health):
        pos = ((loc[0] * game.maze.tile_size) + (game.maze.tile_size // 2) - (size[0] // 2), (loc[1] * game.maze.tile_size) + (game.maze.tile_size // 2) - (size[1] // 2))
        self.game = game
        self.pos = list(pos)
        self.size = size
        self.speed = speed
        self.moving = {'left': False, 'right': False, 'up': False, 'down': False}
        self.dirt_timer = 0
        self.animation = AnimationHandler.create_animation()
        self.knockback_timer = 0
        self.knockback_velocity = [0, 0]
        self.health = health

    def get_rect(self):
        """
        Returns a rect for the entity
        """
        return pygame.Rect(*self.pos, *self.size)
    
    def knockback(self, point, speed):
        """
        Knocks the entity backwards from a point
        """
        # Calculates the displacement between the entity's center and the point
        displacement = ((self.pos[0] + self.size[0] // 2) - point[0], (self.pos[1] + self.size[1] // 2) - point[1])
        # Calculates the magnitude of the displacement using pythagoras' theorem
        magnitude = math.sqrt((displacement[0] ** 2) + (displacement[1] ** 2))
        if magnitude == 0:
            displacement = (1, 1)
            magnitude = math.sqrt((displacement[0] ** 2) + (displacement[1] ** 2))
        # Creates a unit vector by dividing the displacement components by the magnitude. Each component is then multiplied by the speed
        self.knockback_velocity = ((displacement[0] / magnitude) * speed, (displacement[1] / magnitude) * speed)
        self.knockback_timer = KNOCKBACK_TIME
    
    def update(self):
        """
        Updates the entity's position
        """
        # Checks whether the entity is being knocked back and calculates the displacement and decrements the timer if so
        if self.knockback_timer > 0:
            x_displacement = self.knockback_velocity[0] * (self.knockback_timer / KNOCKBACK_TIME) * self.game.multi
            y_displacement = self.knockback_velocity[1] * (self.knockback_timer / KNOCKBACK_TIME) * self.game.multi
            self.knockback_timer -= self.game.dt
        else:
            # Changes the displacement if the entity is not being knocked back based on the direction they are moving
            x_displacement = ((self.moving['right'] * self.speed) - (self.moving['left'] * self.speed)) * self.game.multi
            y_displacement = ((self.moving['down'] * self.speed) - (self.moving['up'] * self.speed)) * self.game.multi

        # Adds the x displacement and checks for collisions with all neighbours
        self.pos[0] += x_displacement
        e_rect = self.get_rect()
        for rect in self.game.maze.get_neighbour_rects(self.game.maze.get_tile(e_rect.center)):
            if e_rect.colliderect(rect):
                if x_displacement > 0:
                    e_rect.right = rect.left
                else:
                    e_rect.left = rect.right
                self.pos[0] = e_rect.x

        # Adds the y displacement and checks for collisions with all neighbours
        self.pos[1] += y_displacement
        e_rect = self.get_rect()
        for rect in self.game.maze.get_neighbour_rects(self.game.maze.get_tile(e_rect.center)):
            if e_rect.colliderect(rect):
                if y_displacement > 0:
                    e_rect.bottom = rect.top
                else:
                    e_rect.top = rect.bottom
                self.pos[1] = e_rect.y

    def draw(self):
        """
        Draws the entity onto the display
        """
        img = self.animation.get_img()
        pos = (self.pos[0] + (self.size[0] // 2) - (img.get_width() // 2) - self.game.camera_displacement[0], self.pos[1] + (self.size[1] // 2) - (img.get_height() // 2) - self.game.camera_displacement[1])
        self.game.display.blit(img, pos)


class Player(Entity):
    def __init__(self, game, loc, size, speed, health):
        super().__init__(game, loc, size, speed, health)
        self.animation.change_animation_library(self.game.animations['player'])
        self.animation.change_animation("idle_forwards")
        self.has_hit = False

    def get_attack_rect(self):
        """
        Returns a rect of the area which is in the player's attack range
        """
        if "sideways" in self.animation.current_animation:
            if self.animation.flip: 
                rect = pygame.Rect(self.pos[0] - PLAYER_ATTACK_RANGE, self.pos[1], PLAYER_ATTACK_RANGE, self.size[1])
            else:
                rect = pygame.Rect(self.pos[0] + self.size[0], self.pos[1], PLAYER_ATTACK_RANGE, self.size[1])
        elif "backwards" in self.animation.current_animation: 
            rect = pygame.Rect(self.pos[0], self.pos[1] - PLAYER_ATTACK_RANGE, self.size[0], PLAYER_ATTACK_RANGE)
        elif "forwards" in self.animation.current_animation: 
            rect = pygame.Rect(self.pos[0], self.pos[1] + self.size[1], self.size[0], PLAYER_ATTACK_RANGE)
        return rect

    def attack(self):
        """
        Changes the player's animation to attack
        """
        if "attack" not in self.animation.current_animation:
            self.has_hit = False
            # Creates a bunch of dirt particles at the player's feet to signal the attack
            for i in range(10):
                ParticleHandler.create_particle("dirt", self.game, (self.pos[0] + (self.size[0] // 2) + random.randint(-5, 5), self.pos[1] + self.size[1] + random.randint(-5, 5)))
            # Changes the player's animation to attack in whatever direction they are facing
            self.animation.change_animation("attack_" + self.animation.current_animation.split("_")[1])

    def hit(self, enemy):
        """
        Hits the player. Called in the enemy class when the enemy hits the player
        """
        # Hits the player if they aren't being knocked back. This gives them invulneribility whilst being knocked back
        if self.knockback_timer <= 0:
            self.health -= 10
            # Creates dust particles which fly off the player to show they've been hit
            for angle in (math.pi * 1/4, math.pi * 2/4, math.pi * 3/4, math.pi, math.pi * 5/4, math.pi * 6/4, math.pi * 7/4, math.pi * 8/4):
                ParticleHandler.create_particle("dust", self.game, (self.pos[0] + (self.size[0] // 2), self.pos[1] + (self.size[1] // 2)), speed=random.random() * 2, angle=angle * random.random())
            # Knocks the player back from the center of the enemy and shakes the screen
            self.knockback((enemy.pos[0] + (enemy.size[0] // 2), enemy.pos[1] + (enemy.size[1] // 2)), 3)
            self.game.shake_screen(5, 0.2)

    def update(self):
        """
        Updates the player's movement, attack, animation and particles
        """
        moving = self.moving.copy()
        if "attack" in self.animation.current_animation:
            if not self.has_hit:
                # Checks whether there are enemies within the player's attack rect and hits them if so
                attack_rect = self.get_attack_rect()
                for enemy in self.game.enemies:
                    if attack_rect.colliderect(enemy.get_rect()):
                        enemy.hit()
                        self.has_hit = True

                # Checks whether the enemy is hitting the treasure and opens it if so
                if attack_rect.colliderect(self.game.treasure.get_rect()) and self.game.treasure.animation.current_animation != "open":
                    # Creates dust particles which fly off the player to show they've hit the treasure
                    for angle in (math.pi * 1/4, math.pi * 2/4, math.pi * 3/4, math.pi, math.pi * 5/4, math.pi * 6/4, math.pi * 7/4, math.pi * 8/4):
                        ParticleHandler.create_particle("dust", self.game, (self.pos[0] + (self.size[0] // 2), self.pos[1] + (self.size[1] // 2)), speed=random.random() * 2, angle=angle * random.random())
                        self.game.treasure.open()

            # Checks whether the attack animation is over and if so, changes the player to an idle animation
            if self.animation.done:
                self.animation.change_animation("idle_" + self.animation.current_animation.split("_")[1])
                self.animation.done = False
            
            # Makes sure the player can't move while they are attacking
            self.moving = {'left': False, 'right': False, 'up': False, 'down': False}

        super().update()
        self.moving = moving

        # Kills the player after their knockback timer is over
        if self.health <= 0 and self.knockback_timer <= 0:
            self.animation.change_animation("death")

        # Changes the player's animations 
        if "attack" not in self.animation.current_animation and "death" not in self.animation.current_animation:
            if self.moving['right'] or self.moving['left']:
                self.animation.change_animation("running_sideways")
            elif self.moving['up']:
                self.animation.change_animation("running_backwards")
            elif self.moving['down']:
                self.animation.change_animation("running_forwards")
            else:
                self.animation.change_animation("idle_" + self.animation.current_animation.split("_")[1])

        # Creates dirt particles under the player's feet if they are running
        self.dirt_timer += self.game.dt
        if "running" in self.animation.current_animation and self.dirt_timer > 0.07:
            self.dirt_timer = 0
            pos = [self.pos[0] + (self.size[0] // 2), self.pos[1] + self.size[1]]
            if self.moving['right']: pos[0] -= 5
            if self.moving['left']: pos[0] += 5
            if self.moving['up']: pos[1] += 5
            if self.moving['down']: pos[1] -= 5
            ParticleHandler.create_particle("dirt", self.game, pos)


class Enemy(Entity):
    def __init__(self, game, pos, size, speed, health):
        super().__init__(game, pos, size, speed, health)
        self.animation.change_animation_library(self.game.animations['slime'])
        self.animation.change_animation("idle")
        self.dirt_timer = 0
        self.path = []
        self.attacking = 0
        self.stunned_timer = 0
        self.slime_particle_timer = 0

    def get_attack_rect(self):
        """
        Returns a rect of the area which is in the enemy's attack range
        """
        return pygame.Rect(self.pos[0] - ENEMY_ATTACK_RANGE, self.pos[1] - ENEMY_ATTACK_RANGE, ENEMY_ATTACK_RANGE * 2 + self.size[0], ENEMY_ATTACK_RANGE * 2 + self.size[1])

    def hit(self):
        """
        Hits the enemy. Called in the player class when they hit the enemy
        """
        # Checks whether they aren't being knocked back and removes their health. This gives the enemy invulnerability when they are being knocked back
        if self.knockback_timer <= 0:
            self.health -= 10
            # Checks whether they have died and changes their animation as well as spawns a bunch of experience
            if self.health <= 0:
                self.animation.change_animation("death")
                for i in range(10):
                    ParticleHandler.create_particle("experience", self.game, (self.pos[0] + (self.size[0] // 2) + random.randint(-5, 5), self.pos[1] + (self.size[1] // 2) + random.randint(-5, 5)), velocity=(random.randint(-4, 4), -random.randint(2, 4)))
        
            # Creates dust particles that fly off from the enemy to show that they've been hit
            for angle in (math.pi * 1/4, math.pi * 2/4, math.pi * 3/4, math.pi, math.pi * 5/4, math.pi * 6/4, math.pi * 7/4, math.pi * 8/4):
                ParticleHandler.create_particle("dust", self.game, (self.pos[0] + (self.size[0] // 2), self.pos[1] + (self.size[1] // 2)), speed=random.random() * 2, angle=angle * random.random())
            
            # Knocks the enemy and shakes the screen
            self.knockback((self.game.player.pos[0] + (self.game.player.size[0] // 2), self.game.player.pos[1] + (self.game.player.size[1] // 2)), 3)
            self.game.shake_screen(5, 0.2)

    def knockback(self, point, velocity):
        """
        Knocks the entity backwards from a point
        """
        super().knockback(point, velocity)
        self.stunned_timer = STUN_TIME

    def calculate_path(self):
        """
        Uses a Breadth First Search to find the shortest path from the enemy to the player
        Each node is formatted as [tile location, parent tile location]
        """
        # Finds the starting tile the enemy is in and the destination tile which the player is in
        starting_tile_loc = self.game.maze.get_loc((self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2))
        destination = self.game.maze.get_loc(self.game.player.pos)

        # Initialises tile list to starting position
        node_list = [(starting_tile_loc, None)]
        explored_tiles = set()

        while True:
            # Checks if the node list is empty as if the node list is empty and target has not been found, there must be no possible path to the target
            if len(node_list) == 0:
                raise Exception("No path from enemy to player")
            
            # Removes the node from the front of the node list
            node = node_list.pop(0)
            explored_tiles.add(node[0])

            # Checks whether the node is the target node
            if node[0] == destination:
                break
            else:
                # Adds the node tile's neighbours to the node list if the tile is a path and it hasn't been explored
                for neighbour in self.game.maze.get_neighbours(self.game.maze.tiles[node[0]], diagonals=False):
                    if neighbour['type'] == "path" and neighbour['loc'] not in explored_tiles and not any(tile_loc[0] == node[0] for tile_loc in node_list):
                        node_list.append((neighbour['loc'], node))

        # Backtracks using the parent of each node to find the shortest path
        shortest_path = []
        while node[1] != None:
            shortest_path.insert(0, node[0])
            node = node[1]

        self.path = shortest_path

    def get_displacement_from_center(self, loc):
        """
        Returns the displacement from the center of a given tile location
        """
        return ((loc[0] * self.game.maze.tile_size) + (self.game.maze.tile_size // 2) - (self.pos[0] + self.size[0] // 2), (loc[1] * self.game.maze.tile_size) + (self.game.maze.tile_size // 2) - (self.pos[1] + self.size[1] // 2))

    def update(self):
        """
        Updates the player's movement, attack, animation and particles
        """
        self.moving = {'left': False, 'right': False, 'up': False, 'down': False}

        if self.stunned_timer <= 0 and not self.animation.current_animation == "death":
            # Checks whether the enemy is close to the center of a tile and refreshes their path if so
            displacement = self.get_displacement_from_center(self.game.maze.get_loc(self.pos))
            if abs(displacement[0]) <= MAX_DISTANCE and abs(displacement[1]) <= MAX_DISTANCE or len(self.path) == 0:
                self.calculate_path()

            # Checks whether the enemy is near the center of a tile and if so, removes the tile from the path 
            if len(self.path) != 0:
                displacement = self.get_displacement_from_center(self.path[0])
                if abs(displacement[0]) <= MAX_DISTANCE and abs(displacement[1]) <= MAX_DISTANCE:
                    self.path.remove(self.path[0])
            else:
                # Moves the enemy directly towards the player as they must be on the same tile
                displacement = self.get_displacement_from_center(self.game.maze.get_loc(self.game.player.pos))


            # Gets the displacement from the center of the tile
            if len(self.path) != 0:
                displacement = self.get_displacement_from_center(self.path[0])
            else:
                # Checks whether the enemy is within attacking range of the player and attacks if so or gets the displacement from the enemy to the player
                attack_rect = self.get_attack_rect()
                if attack_rect.colliderect(self.game.player.get_rect()):
                    self.game.player.hit(self)
                    self.stunned_timer = STUN_TIME
                    displacement = (0, 0)
                else:
                    displacement = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
            
            # Determines the direction the enemy needs to move based on their displacement from their target
            if displacement[0] < -MAX_DISTANCE:
                self.moving['left'] = True
            if displacement[0] > MAX_DISTANCE:
                self.moving['right'] = True
            if displacement[1] < -MAX_DISTANCE:
                self.moving['up'] = True
            if displacement[1] > MAX_DISTANCE:
                self.moving['down'] = True

        # Decrements the stun timer if the knockback timer is over. This means the stun only starts when the knockback has finished
        elif self.knockback_timer <= 0:
            self.stunned_timer -= self.game.dt
   
        super().update()

        # Updates the enemy's animation 
        if not self.animation.current_animation == "death":
            if self.moving['right'] or self.moving['left'] or self.moving['up'] or self.moving['down']:
                self.animation.change_animation("running")
            else:
                self.animation.change_animation("idle")
        elif self.animation.done:
            self.kill()

        # Creates dirt particles under the enemy's feet if they are running
        self.dirt_timer += self.game.multi
        if "running" in self.animation.current_animation and self.dirt_timer > 4:
            self.dirt_timer = 0
            ParticleHandler.create_particle("dirt", self.game, (self.pos[0] + (self.size[0] // 2), self.pos[1] + (self.size[1] // 2)))

        # Creates dirt particles under the enemy's feet if they are running
        self.slime_particle_timer += self.game.multi
        if "running" in self.animation.current_animation and self.slime_particle_timer > 5:
            self.slime_particle_timer = 0
            ParticleHandler.create_particle("slime", self.game, (self.pos[0] + (self.size[0] // 2), self.pos[1] + (self.size[1] // 2)), parent=self, variance=(random.randint(-10, 10), random.randint(-3, 3)))
        
    def kill(self):
        """
        Removes the enemy's animation and then removes it from the enemies list
        """
        self.game.killed += 1
        AnimationHandler.kill_animation(self.animation)
        self.game.enemies.remove(self)

        
