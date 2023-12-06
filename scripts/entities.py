import random
import math

import pygame

from scripts.animations import AnimationHandler
from scripts.effects import ParticleHandler, Spike
from scripts.utils import AudioPlayer, get_vector

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
# This is the height of the rect used to detect collisions
FEET_HEIGHT = 4
# This is the speed of the player when dashing (keep as float)
DASHING_VELOCITY = 6.0
# This is how long the player dashes for
DASHING_TIMER = 0.2
# This is how long the player explodes for
EXPLOSION_TIMER = 0.75
# This is how long the player sweeps for
SPIRAL_TIMER = 0.75

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
        self.glow_timer = random.uniform(0, 2 * math.pi)
        self.special_attack = {'name': None}

    def get_center(self):
        """
        Returns the center of an entity
        """
        return (self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[0] // 2)

    def get_rect(self):
        """
        Returns a rect for the entity
        """
        return pygame.Rect(*self.pos, *self.size)
    
    def get_feet_rect(self):
        """
        Returns a rect at the entity's feet
        """
        return pygame.Rect(self.pos[0], self.pos[1] + self.size[1] - FEET_HEIGHT, self.size[0], FEET_HEIGHT)
    
    def knockback(self, point, speed):
        """
        Knocks the entity backwards from a point
        """
        # Sets the velocity for the entity's knockback and changes the timer
        self.knockback_velocity = get_vector((self.get_center(), point), speed)
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
        elif self.special_attack['name'] != None:
            x_displacement = self.special_attack['vel'][0] * self.game.multi
            y_displacement = self.special_attack['vel'][1] * self.game.multi
        else:
            # Changes the displacement if the entity is not being knocked back based on the direction they are moving
            x_displacement = ((self.moving['right'] * self.speed) - (self.moving['left'] * self.speed)) * self.game.multi * (0.75 if "attack" in self.animation.current_animation else 1)
            y_displacement = ((self.moving['down'] * self.speed) - (self.moving['up'] * self.speed)) * self.game.multi * (0.75 if "attack" in self.animation.current_animation else 1)

        # Adds the x displacement and checks for collisions with all neighbours
        self.pos[0] += x_displacement
        feet_rect = self.get_feet_rect()
        neighbours = self.game.maze.get_neighbour_rects(self.game.maze.get_tile(feet_rect.center))
        for rect in neighbours:
            if feet_rect.colliderect(rect):
                if x_displacement > 0:
                    feet_rect.right = rect.left
                else:
                    feet_rect.left = rect.right
                self.pos[0] = feet_rect.x

        # Adds the y displacement and checks for collisions with all neighbours
        self.pos[1] += y_displacement
        feet_rect = self.get_feet_rect()
        for rect in neighbours:
            if feet_rect.colliderect(rect):
                if y_displacement > 0:
                    feet_rect.bottom = rect.top
                else:
                    feet_rect.top = rect.bottom
                self.pos[1] = feet_rect.bottom - self.size[1]

        self.glow_timer = (self.glow_timer + self.game.dt * 2) % (2 * math.pi)

    def draw(self):
        """
        Draws the entity onto the display
        """
        img = self.animation.get_img()
        center = self.get_center()
        pos = (center[0] - (img.get_width() // 2) - self.game.camera_displacement[0], center[1] - (img.get_height() // 2) - self.game.camera_displacement[1])
        self.game.display.blit(img, pos)
        self.game.glow(center, (205, 205, 255), max(self.size) + 8 + round(5 * math.sin(self.glow_timer) + random.random()))


class Player(Entity):
    def __init__(self, game, loc, size, speed, health):
        super().__init__(game, loc, size, speed, health)
        self.animation.change_animation_library(self.game.animations['player'])
        self.animation.change_animation("idle_forwards")
        self.has_hit = False

    def dash(self):
        """
        Makes the player dash forwards
        """
        if self.special_attack['name'] == None and "attack" not in self.animation.current_animation and self.game.special_attacks[0] != 0:
            center = self.get_center()
            if "forwards" in self.animation.current_animation:
                destination = (center[0], center[1] + 1)
            elif "backwards" in self.animation.current_animation:
                destination = (center[0], center[1] - 1)
            elif self.animation.flip:
                destination = (center[0] - 1, center[1])
            else:
                destination = (center[0] + 1, center[1])
            self.special_attack['name'] = "dash"
            self.special_attack['vel'] = get_vector((destination, center), DASHING_VELOCITY)
            self.special_attack['last_animation'] = self.animation.current_animation
            self.special_attack['timer'] = DASHING_TIMER
            self.special_attack['particle_timer'] = 0
            self.animation.change_animation("dashing")
            self.game.special_attacks[0] -= 1

    def spiral(self):
        """
        Makes the player do the spiral attack
        """
        if self.special_attack['name'] == None and "attack" not in self.animation.current_animation and self.game.special_attacks[1] != 0:
            self.special_attack['name'] = "spiral"
            self.special_attack['vel'] = [0, 0]
            self.special_attack['timer'] = SPIRAL_TIMER
            self.special_attack['spike_timer'] = 0
            self.animation.change_animation("idle_" + self.animation.current_animation.split("_")[1])
            self.game.special_attacks[1] -= 1

    def explode(self):
        """
        Makes the player do the explosion attack
        """
        if self.special_attack['name'] == None and "attack" not in self.animation.current_animation and self.game.special_attacks[2] != 0:
            self.special_attack['name'] = "explode"
            self.special_attack['vel'] = [0, 0]
            self.special_attack['timer'] = EXPLOSION_TIMER
            self.special_attack['spike_timer'] = 0
            self.special_attack['explosions'] = 0
            self.animation.change_animation("idle_" + self.animation.current_animation.split("_")[1])
            self.game.special_attacks[2] -= 1

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
        else:
            center = self.get_center()
            rect = pygame.Rect(0, 0, self.size[0] + 5, self.size[1] + 5)
            rect.center = center
        return rect

    def attack(self):
        """
        Changes the player's animation to attack
        """
        if "attack" not in self.animation.current_animation and self.special_attack['name'] == None:
            self.has_hit = False
            # Creates a bunch of dirt particles at the player's feet to signal the attack
            center = self.get_center()
            for i in range(10):
                ParticleHandler.create_particle("dirt", self.game, (center[0] + random.randint(-5, 5), self.pos[1] + self.size[1] + random.randint(-5, 5)))
            # Changes the player's animation to attack in whatever direction they are facing and plays the attack sound
            self.animation.change_animation("attack_" + self.animation.current_animation.split("_")[1])
            AudioPlayer.play_sound("player_attack")

    def hit(self, enemy):
        """
        Hits the player. Called in the enemy class when the enemy hits the player
        """
        # Hits the player if they aren't being knocked back. This gives them invulneribility whilst being knocked back
        if self.knockback_timer <= 0:
            self.health -= 10
            # Creates dust particles which fly off the player to show they've been hit
            center = self.get_center()
            for angle in (math.pi * 1/4, math.pi * 2/4, math.pi * 3/4, math.pi, math.pi * 5/4, math.pi * 6/4, math.pi * 7/4, math.pi * 8/4):
                ParticleHandler.create_particle("dust", self.game, center, speed=random.random() * 2, angle=angle * random.random())
            # Knocks the player back from the center of the enemy, shakes the screen and plays a sound
            self.knockback(enemy.get_center(), 3)
            self.game.shake_screen(10, 0.2)
            AudioPlayer.play_sound("hit")

    def update(self):
        """
        Updates the player's movement, attack, animation and particles
        """
        super().update()
        if "attack" in self.animation.current_animation or self.special_attack['name'] == "dash":
            if not self.has_hit or self.special_attack['name'] == "dash":
                # Checks whether there are enemies within the player's attack rect and hits them if so
                attack_rect = self.get_attack_rect()
                for enemy in self.game.enemies:
                    if attack_rect.colliderect(enemy.get_rect()):
                        enemy.hit()
                        self.has_hit = True

                # Checks whether the enemy is hitting the treasure and opens it if so
                if attack_rect.colliderect(self.game.treasure.get_rect()) and self.game.treasure.animation.current_animation != "open":
                    # Creates dust particles which fly off the player to show they've hit the treasure
                    center = self.get_center()
                    for i in range(8):
                        ParticleHandler.create_particle("dust", self.game, center, speed=random.random() * 2, angle=math.pi * (i + 1)/4  * random.random())
                        self.game.treasure.open()

            # Checks whether the attack animation is over and if so, changes the player to an idle animation
            if self.animation.done and self.special_attack['name'] != "dash":
                self.animation.change_animation("idle_" + self.animation.current_animation.split("_")[1])
                self.animation.done = False

        # Updates the player's special attack
        if self.special_attack['name'] != None:
            self.special_attack['timer'] = max(self.special_attack['timer'] - self.game.dt, 0)

            # Creates particles if the special attack is dash
            if self.special_attack['name'] == "dash":
                self.special_attack['particle_timer'] = max(self.special_attack['particle_timer'] - self.game.dt, 0)
                if self.special_attack['particle_timer'] == 0:
                    ParticleHandler.create_particle("player_dashing", self.game, self.get_center())
                    self.special_attack['particle_timer'] = 0.02

            # Creates spikes if the special attack is explode
            if self.special_attack['name'] == "explode":
                self.special_attack['spike_timer'] = max(self.special_attack['spike_timer'] - self.game.dt, 0)
                if self.special_attack['spike_timer'] == 0:
                    for i in range(25):
                        self.game.spikes.append(Spike(self.game, self.get_center(), math.pi * 2 * i/10 + random.uniform(-0.3, 0.3), random.uniform(1.5, 2.5), (140, 0, 0), can_damage=True))
                    self.special_attack['spike_timer'] = 0.25

            # Creates spikes if the special attack is spiral
            if self.special_attack['name'] == "spiral":
                self.special_attack['spike_timer'] = max(self.special_attack['spike_timer'] - self.game.dt, 0)
                angle = (self.special_attack['timer'] / SPIRAL_TIMER) * 2 * math.pi
                angle2 = (angle + math.pi) % (2 * math.pi)
                if self.special_attack['spike_timer'] == 0:
                    center = self.get_center()
                    pos = (center[0] + math.cos(angle) * 20, center[1] + math.sin(angle) * 20)
                    pos2 = (center[0] + math.cos(angle2) * 20, center[1] + math.sin(angle2) * 20)
                    self.game.spikes.append(Spike(self.game, pos2, angle2 + random.uniform(-0.5, 0.5), random.uniform(1.5, 2.5), (50, 125, 140), can_damage=True))
                    self.game.spikes.append(Spike(self.game, pos, angle + random.uniform(-0.5, 0.5), random.uniform(1.5, 2.5), (50, 125, 140), can_damage=True))
                    self.special_attack['spike_timer'] = 0.01


            # Ends the player's special attack if time has run out
            if self.special_attack['timer'] == 0:
                if self.special_attack['name'] == "dash":
                    self.animation.change_animation(self.special_attack['last_animation'])
                    for i in range(10):
                        self.game.spikes.append(Spike(self.game, self.get_center(), math.pi * 2 * i/10 + random.uniform(-0.3, 0.3), 2, (20, 16, 32)))
                self.special_attack['name'] = None

        # Kills the player after their knockback timer is over
        if self.health <= 0 and self.knockback_timer <= 0 and self.animation.current_animation != "death":
            self.animation.change_animation("death")
            AudioPlayer.play_sound("player_death")

        # Changes the player's animations 
        if "attack" not in self.animation.current_animation and self.animation.current_animation != "death" and self.special_attack['name'] == None:
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
        if "running" in self.animation.current_animation and self.dirt_timer > 0.07 and self.special_attack['name'] == None:
            self.dirt_timer = 0
            pos = [self.pos[0] + (self.size[0] // 2), self.pos[1] + self.size[1] - 5]
            if self.moving['right']: pos[0] -= 5
            if self.moving['left']: pos[0] += 5
            if self.moving['up']: pos[1] += 5
            if self.moving['down']: pos[1] -= 5
            ParticleHandler.create_particle("dirt", self.game, pos)


class Enemy(Entity):
    def __init__(self, game, pos, size, speed, health, color):
        super().__init__(game, pos, size, speed, health)
        self.color = color
        self.animation.change_animation_library(self.game.animations[self.color + '_slime'])
        self.animation.change_animation("idle")
        self.path = []
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
                center = self.get_center()
                for i in range(10):
                    ParticleHandler.create_particle("experience", self.game, (center[0] + random.randint(-5, 5), center[1] + random.randint(-5, 5)), velocity=(random.uniform(2, -2), random.uniform(-4, -2)))
        
            # Creates dust particles that fly off from the enemy to show that they've been hit
            for angle in (math.pi * 1/4, math.pi * 2/4, math.pi * 3/4, math.pi, math.pi * 5/4, math.pi * 6/4, math.pi * 7/4, math.pi * 8/4):
                ParticleHandler.create_particle("dust", self.game, self.get_center(), speed=random.random() * 2, angle=angle * random.random())
            
            # Knocks the enemy back, shakes the screen and plays a sound
            self.knockback(self.game.player.get_center(), 3)
            self.game.shake_screen(10, 0.2)
            AudioPlayer.play_sound("hit")

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
        starting_tile_loc = self.game.maze.get_loc(self.get_center())
        destination = self.game.maze.get_loc((self.game.player.pos[0] + self.game.player.size[0] // 2, self.game.player.pos[1] + self.game.player.size[1] - (FEET_HEIGHT // 2)))

        # Initialises tile list to starting position
        node_list = [(starting_tile_loc, None)]
        explored_tiles = set()

        while True:
            # Checks if the node list is empty as if the node list is empty and target has not been found, there must be no possible path to the target
            if len(node_list) == 0:
                self.kill()
                return
            
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
        center = self.get_center()
        return ((loc[0] * self.game.maze.tile_size) + (self.game.maze.tile_size // 2) - center[0], (loc[1] * self.game.maze.tile_size) + (self.game.maze.tile_size // 2) - center[1])

    def update(self):
        """
        Updates the player's movement, attack, animation and particles
        """
        self.moving = {'left': False, 'right': False, 'up': False, 'down': False}

        if self.stunned_timer <= 0 and not self.animation.current_animation == "death":
            # Checks whether the enemy is close to the center of a tile and refreshes their path if so
            displacement = self.get_displacement_from_center(self.game.maze.get_loc(self.get_center()))
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
                    AudioPlayer.play_sound("enemy_attack")
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
                if self.moving['right']: self.animation.flip = False
                if self.moving['left']: self.animation.flip = True
            else:
                self.animation.change_animation("idle")
        elif self.animation.done:
            self.kill()

        # Creates dirt particles under the enemy's feet if they are running
        self.dirt_timer += self.game.multi
        if "running" in self.animation.current_animation and self.dirt_timer > 4:
            self.dirt_timer = 0
            ParticleHandler.create_particle("dirt", self.game, self.get_center())

        # Creates dirt particles under the enemy's feet if they are running
        self.slime_particle_timer += self.game.multi
        if "running" in self.animation.current_animation and self.slime_particle_timer > 5:
            self.slime_particle_timer = 0
            ParticleHandler.create_particle("slime", self.game, self.get_center(), parent=self, variance=(random.randint(-10, 10), random.randint(-3, 3)), color=self.color)
        
    def kill(self):
        """
        Removes the enemy's animation and then removes it from the enemies list
        """
        self.game.killed += 1
        AnimationHandler.kill_animation(self.animation)
        self.game.enemies.remove(self)
        AudioPlayer.play_sound("enemy_death")

        
