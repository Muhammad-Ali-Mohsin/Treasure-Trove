import math
import random
import pygame

from scripts.animations import AnimationHandler
from scripts.utils import AudioPlayer, get_vector

# Particle Constants
EXPERIENCE_TARGET_POINT = (17, 10)
GOLD_TARGET_POINT = (15, 40)
DASH_TARGET_POINT = (25, 210)
SPIRAL_TARGET_POINT = (68, 200)
EXPLOSION_TARGET_POINT = (105, 200)
DISTANCE_FROM_TARGET = 2

# Spikes Constants
SPIKE_WIDTH_MULTI = 0.75
SPIKE_HEIGHT_MULTI = 3

class Particle:
    def __init__(self, game, pos):
        self.game = game
        self.pos = list(pos)
        self.animation = AnimationHandler.create_animation()
        self.timer = None

    def move(self):
        pass

    def draw(self):
        """
        Draws the particle onto the display
        """
        img = self.animation.get_img()
        pos = (self.pos[0] - (img.get_width() // 2) - self.game.camera_displacement[0], self.pos[1] - (img.get_height() // 2) - self.game.camera_displacement[1])
        self.game.display.blit(img, pos)

class StatParticle(Particle):
    def __init__(self, game, pos, kwargs):
        super().__init__(game, pos)
        self.pos = [pos[0] - self.game.camera_displacement[0], pos[1] - self.game.camera_displacement[1]]
        self.velocity = list(kwargs['velocity'])
        self.timer = 10
        self.travelling_up = False
        self.target = None

    def move(self):
        """
        Moves the particle towards the target point on the screen
        """
        # Moves the particle according to its velocity
        self.pos[0] += self.velocity[0] * self.game.multi
        self.pos[1] += self.velocity[1] * self.game.multi

        # Applies gravity to the particle
        if not self.travelling_up:
            self.velocity[1] = min(self.velocity[1] + (self.game.multi * 0.1), 5)
        
        # Makes the particle start travelling to the target if it is sufficiently low on the screen
        if self.pos[1] > 220:
            self.velocity = get_vector((self.target, self.pos), 3)
            self.travelling_up = True

        # Checks to see if the particle has arrived at the target
        displacement = (self.target[0] - self.pos[0], self.target[1] - self.pos[1])
        if abs(displacement[0]) <= DISTANCE_FROM_TARGET and abs(displacement[1]) < DISTANCE_FROM_TARGET:
            if self.game.player.animation.current_animation != "death":
                self.target_reached()
            self.timer = 0

    def target_reached(self):
        pass

    def draw(self):
        """
        Blits the image onto the surface without camera displacement and adds a glow effect
        """
        img = self.animation.get_img()
        pos = (self.pos[0] - (img.get_width() // 2), self.pos[1] - (img.get_height() // 2))
        self.game.display.blit(img, pos)
        self.game.glow((self.pos[0] + self.game.camera_displacement[0], self.pos[1] + self.game.camera_displacement[1]), (205, 205, 255), 10)


class Experience(StatParticle):
    def __init__(self, game, pos, kwargs):
        super().__init__(game, pos, kwargs)
        self.target = EXPERIENCE_TARGET_POINT
        self.animation.change_animation_library(self.game.animations['experience'])
        self.animation.frame = random.randint(0, len(self.animation.animation_library[self.animation.current_animation]['images']) - 1)
        AudioPlayer.play_sound("experience")

    def target_reached(self):
        super().target_reached()
        # Adds health to the player
        self.game.player.health = min(100, self.game.player.health + 0.5)
        AudioPlayer.play_sound("health")


class Gold(StatParticle):
    def __init__(self, game, pos, kwargs):
        super().__init__(game, pos, kwargs)
        self.target = GOLD_TARGET_POINT
        self.animation.change_animation_library(self.game.animations['gold'])
        AudioPlayer.play_sound("treasure")

    def target_reached(self):
        super().target_reached()
        # Adds gold to the player
        self.game.gold += random.randint(40, 60)
        AudioPlayer.play_sound("gold")


class PlusOne(StatParticle):
    def __init__(self, game, pos, kwargs):
        super().__init__(game, pos, kwargs)
        self.attack_type = kwargs['attack_type']
        self.target = (DASH_TARGET_POINT, SPIRAL_TARGET_POINT, EXPLOSION_TARGET_POINT)[self.attack_type]
        self.animation.change_animation_library(self.game.animations['plus_one'])
        AudioPlayer.play_sound("plus_one_spawn")

    def target_reached(self):
        super().target_reached()
        # Adds special attacks to the player
        self.game.special_attacks[self.attack_type] = min(5, self.game.special_attacks[self.attack_type] + 1)
        AudioPlayer.play_sound("plus_one")


class Dirt(Particle):
    def __init__(self, game, pos, kwargs):
        super().__init__(game, pos)
        self.animation.change_animation_library(self.game.animations['dirt'])

class PlayerDashing(Particle):
    def __init__(self, game, pos, kwargs):
        super().__init__(game, pos)
        self.animation.change_animation_library(self.game.animations['player_dashing'])


class Leaf(Particle):
    def __init__(self, game, pos, kwargs):
        super().__init__(game, pos)
        self.speed = kwargs['speed']
        self.animation.change_animation_library(self.game.animations['leaves'])

    def move(self):
        """
        Moves the leaf according to the wind intensity and a sine wave
        """
        self.pos[0] += (math.sin(2 * math.pi * (self.animation.frame / 10)) * self.speed * self.game.multi) + (2 * self.game.wind_intensity * self.game.multi)
        self.pos[1] += self.speed * self.game.multi


class Slime(Particle):
    def __init__(self, game, pos, kwargs):
        super().__init__(game, pos)
        self.parent = kwargs['parent']
        self.displacement = list(kwargs['displacement'])
        self.animation.change_animation_library(self.game.animations[kwargs['color'] + '_slime_particle'])

    def move(self):
        self.pos = (self.parent.pos[0] + (self.parent.size[0] // 2) + self.displacement[0], self.parent.pos[1] + self.displacement[1])
        self.displacement[1] = self.displacement[1] - (0.2 * self.game.multi)


class Dust(Particle):
    def __init__(self, game, pos, kwargs):
        super().__init__(game, pos)
        self.speed = kwargs['speed']
        self.angle = kwargs['angle']
        self.animation.change_animation_library(self.game.animations['dust'])

    def move(self):
        self.pos[0] += math.cos(self.angle) * self.speed * self.game.multi
        self.pos[1] += math.sin(self.angle) * self.speed * self.game.multi

class Bee(Particle):
    def __init__(self, game, pos, kwargs):
        super().__init__(game, pos)
        self.speed = kwargs['speed']
        self.animation.change_animation_library(self.game.animations['bee'])
        self.timer = 20
        self.angle = random.uniform(0, 2 * math.pi)
        self.angular_speed = 0

    def move(self):
        # Uses the angle to calculate x and y displacements before adding them to the position
        self.pos[0] += math.sin(self.angle) * self.speed * self.game.multi
        self.pos[1] += math.cos(self.angle) * self.speed * self.game.multi

        # Adds the angular speed to the angle
        self.angle += self.angular_speed * self.game.multi

        # Randomly changes the angular speed (a smaller speed means a bigger radius and a bigger speed means a smaller radius)
        if random.random() < 0.01:
            self.angular_speed = random.uniform(0, 0.1)

    def draw(self):
        img = self.animation.get_img()
        # Decreases the opacity of the image down to 0 within te last 5 seconds of its life
        if self.timer < 5: img.set_alpha(self.timer / 5 * 255)
        pos = (self.pos[0] - (img.get_width() // 2) - self.game.camera_displacement[0], self.pos[1] - (img.get_height() // 2) - self.game.camera_displacement[1])
        # Calculates the luminosity of the light given off by the bee/firefly which increases to a maximum and then to a minimum over 20 seconds according to a sine wave
        luminosity = math.sin(self.timer / 20 * math.pi)
        self.game.glow(self.pos, (round(205 * luminosity), round(205 * luminosity), round(255 * luminosity)), 20)
        self.game.glow(self.pos, (round(255 * luminosity), round(255 * luminosity), round(255 * luminosity)), 8)
        self.game.display.blit(img, pos)


class ParticleHandler:
    particles = []
    particle_types = {'dirt': Dirt, 'leaf': Leaf, 'experience': Experience, 'slime': Slime, 'dust': Dust, 'gold': Gold, 'bee': Bee, 'player_dashing': PlayerDashing, 'plus_one': PlusOne}

    def update():
        """
        Moves all the particles and removes them if they are finished
        """
        killed = []
        for particle in ParticleHandler.particles:
            particle.move()
            particle.draw()
            # Checks whether the particle uses a timer and decrements it if it does
            if particle.timer != None:
                particle.timer -= particle.game.dt
                # Removes the particle if its timer is complete
                if particle.timer <= 0:
                    killed.append(particle)
            # Removes the particle if its animation is complete
            elif particle.animation.done:
                killed.append(particle)
        
        for particle in killed:
            ParticleHandler.kill_particle(particle)

    def create_particle(type, game, pos, **kwargs):
        """
        Creates a particle
        """
        particle = ParticleHandler.particle_types[type](game, pos, kwargs)
        ParticleHandler.particles.append(particle)
        
    def kill_particle(particle):
        """
        Deletes the particle from the animation list and then deletes it from the particle list
        """
        AnimationHandler.kill_animation(particle.animation)
        ParticleHandler.particles.remove(particle)


colors = {'blue': (50, 125, 140), 'red': (140, 0, 0), 'purple': (20, 16, 32)}

class Spike:
    def __init__(self, game, pos, angle, speed, color_id):
        self.game = game
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed
        self.color_id = color_id
        self.color = colors[color_id]

    def get_rect(self):
        return pygame.Rect(*self.pos, self.speed * SPIKE_HEIGHT_MULTI, self.speed * SPIKE_HEIGHT_MULTI)

    def update(self):
        """
        Moves the spike and hits any enemies if it is colliding with them
        """
        self.pos[0] += math.cos(self.angle) * self.speed * self.game.multi
        self.pos[1] += math.sin(self.angle) * self.speed * self.game.multi
        # Decreases the speed of the spike over time
        self.speed -= self.game.dt * 3

        rect = self.get_rect()
        for enemy in self.game.enemies:
            if rect.colliderect(enemy.get_rect()):
                enemy.hit(self.color_id)

    def draw(self):
        """
        Draws the spike onto the display
        """
        # Calculates the position of the spike on the screen
        pos = (self.pos[0] - self.game.camera_displacement[0], self.pos[1] - self.game.camera_displacement[1])
        # Uses the angle and size of the spike to calculate the four corners of the spike which is a quadrilateral
        # This is then connected with a line through pygame.draw.polygon to draw te spike
        pygame.draw.polygon(self.game.display, self.color, [
            (pos[0] + math.cos(self.angle) * self.speed * SPIKE_HEIGHT_MULTI, pos[1] + math.sin(self.angle) * self.speed * SPIKE_HEIGHT_MULTI),
            (pos[0] + math.cos(self.angle + math.pi * 0.5) * self.speed * SPIKE_WIDTH_MULTI, pos[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * SPIKE_WIDTH_MULTI),
            (pos[0] + math.cos(self.angle + math.pi) * self.speed * SPIKE_HEIGHT_MULTI, pos[1] + math.sin(self.angle + math.pi) * self.speed * SPIKE_HEIGHT_MULTI),
            (pos[0] + math.cos(self.angle + math.pi * 1.5) * self.speed * SPIKE_WIDTH_MULTI, pos[1] + math.sin(self.angle - math.pi * 0.5) * self.speed * SPIKE_WIDTH_MULTI),
        ])
        # Adds a light to the spikes
        self.game.glow(self.pos, (205, 205, 255), 7.5 * self.speed)