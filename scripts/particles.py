import math
import random

from scripts.animations import AnimationHandler

EXPERIENCE_TARGET_POINT = (17, 10)
GOLD_TARGET_POINT = (15, 40)
DISTANCE_FROM_TARGET = 2


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


class Dirt(Particle):
    def __init__(self, game, pos, kwargs):
        super().__init__(game, pos)
        self.animation.change_animation_library(self.game.animations['dirt'])


class Leaf(Particle):
    def __init__(self, game, pos, kwargs):
        super().__init__(game, pos)
        self.speed = kwargs['speed']
        self.animation.change_animation_library(self.game.animations['leaves'])

    def move(self):
        self.pos[0] += math.sin(2 * math.pi * (self.animation.timer / 0.9)) * (self.game.wind_intensity * 3) * self.game.multi
        self.pos[1] += self.speed * self.game.multi


class Experience(Particle):
    def __init__(self, game, pos, kwargs):
        super().__init__(game, pos)
        self.pos = [pos[0] - self.game.camera_displacement[0], pos[1] - self.game.camera_displacement[1]]
        self.velocity = [kwargs['velocity'][0] * 0.3, kwargs['velocity'][1]]
        self.timer = 10
        self.travelling_up = False
        self.animation.change_animation_library(self.game.animations['experience'])
        self.animation.frame = random.randint(0, len(self.animation.animation_library[self.animation.current_animation]['images']) - 1)

    def move(self):
        self.pos[0] += self.velocity[0] * self.game.multi
        self.pos[1] += self.velocity[1] * self.game.multi
        if not self.travelling_up:
            self.velocity[1] = min(self.velocity[1] + (self.game.multi * 0.1), 5)

        displacement = (EXPERIENCE_TARGET_POINT[0] - self.pos[0], EXPERIENCE_TARGET_POINT[1] - self.pos[1])

        if self.pos[1] > 220:
            magnitude = math.sqrt((displacement[0] ** 2) + (displacement[1] ** 2))
            self.velocity = ((displacement[0] / magnitude) * 3, (displacement[1] / magnitude) * 3)

        elif self.pos[1] > 140 and not self.travelling_up:
            self.velocity[1] = self.velocity[1] - (self.game.multi * 0.4)
            self.travelling_up = True

        if abs(displacement[0]) <= DISTANCE_FROM_TARGET and abs(displacement[1]) < DISTANCE_FROM_TARGET:
            if self.game.player.animation.current_animation != "death":
                self.game.player.health = min(100, self.game.player.health + 0.5)
            self.timer = 0

    def draw(self):
        img = self.animation.get_img()
        pos = (self.pos[0] - (img.get_width() // 2), self.pos[1] - (img.get_height() // 2))
        self.game.display.blit(img, pos)


class Slime(Particle):
    def __init__(self, game, pos, kwargs):
        super().__init__(game, pos)
        self.parent = kwargs['parent']
        self.variance = list(kwargs['variance'])
        self.animation.change_animation_library(self.game.animations['slime_particle'])

    def move(self):
        self.pos = (self.parent.pos[0] + (self.parent.size[0] // 2) + self.variance[0], self.parent.pos[1] + self.variance[1])
        self.variance[1] = self.variance[1] - (0.2 * self.game.multi)

class Gold(Particle):
    def __init__(self, game, pos, kwargs):
        super().__init__(game, pos)
        self.pos = [pos[0] - self.game.camera_displacement[0], pos[1] - self.game.camera_displacement[1]]
        self.velocity = [kwargs['velocity'][0] * 0.3, kwargs['velocity'][1]]
        self.timer = 10
        self.travelling_up = False
        self.animation.change_animation_library(self.game.animations['gold'])

    def move(self):
        self.pos[0] += self.velocity[0] * self.game.multi
        self.pos[1] += self.velocity[1] * self.game.multi
        if not self.travelling_up:
            self.velocity[1] = min(self.velocity[1] + (self.game.multi * 0.1), 5)

        displacement = (GOLD_TARGET_POINT[0] - self.pos[0], GOLD_TARGET_POINT[1] - self.pos[1])

        if self.pos[1] > 220:
            magnitude = math.sqrt((displacement[0] ** 2) + (displacement[1] ** 2))
            self.velocity = ((displacement[0] / magnitude) * 3, (displacement[1] / magnitude) * 3)

        elif self.pos[1] > 140 and not self.travelling_up:
            self.velocity[1] = self.velocity[1] - (self.game.multi * 0.4)
            self.travelling_up = True

        if abs(displacement[0]) <= DISTANCE_FROM_TARGET and abs(displacement[1]) < DISTANCE_FROM_TARGET:
            self.game.gold += random.randint(40, 60)
            self.timer = 0

    def draw(self):
        img = self.animation.get_img()
        pos = (self.pos[0] - (img.get_width() // 2), self.pos[1] - (img.get_height() // 2))
        self.game.display.blit(img, pos)

class Dust(Particle):
    def __init__(self, game, pos, kwargs):
        super().__init__(game, pos)
        self.speed = kwargs['speed']
        self.angle = kwargs['angle']
        self.animation.change_animation_library(self.game.animations['dust'])

    def move(self):
        self.pos[0] += math.cos(self.angle) * self.speed * self.game.multi
        self.pos[1] += math.sin(self.angle) * self.speed * self.game.multi


class ParticleHandler:
    particles = []
    particle_types = {'dirt': Dirt, 'leaf': Leaf, 'experience': Experience, 'slime': Slime, 'dust': Dust, 'gold': Gold}

    def update():
        """
        Moves all the particles and removes them if their animation has finished
        """
        killed = []
        for particle in ParticleHandler.particles:
            particle.move()
            particle.draw()
            if particle.timer != None:
                particle.timer -= particle.game.dt
                if particle.timer <= 0:
                    killed.append(particle)
            elif particle.animation.done:
                killed.append(particle)
        
        for particle in killed:
            ParticleHandler.kill_particle(particle)

    def create_particle(type, game, pos, **kwargs):
        if type in ParticleHandler.particle_types:
            particle = ParticleHandler.particle_types[type](game, pos, kwargs)
            ParticleHandler.particles.append(particle)
        else:
            raise Exception("Particle not found")
        
    def kill_particle(particle):
        """
        Deletes the particle from the animation list and then deletes it from the particle list
        """
        AnimationHandler.kill_animation(particle.animation)
        ParticleHandler.particles.remove(particle)