import pygame
import math


diamondWidth = 80
diamondHeight = 100

class Spark:

    instances = []

    def update():
        """
        Moves all the sparks and removes them if their timer is over
        """
        killed = []
        for spark in Spark.instances:
            spark.move()
            spark.draw()
            if spark.timer != None:
                spark.timer -= 1
                if spark.timer <= 0:
                    killed.append(spark)
        
        for spark in killed:
            spark.kill()

    def __init__(self, game, pos, origin, speed):
        self.game = game
        self.pos = list(pos)
        self.origin = tuple(origin)
        self.timer = None
        Spark.instances.append(self)
        displacement = (origin[0] - self.pos[0], origin[1] - self.pos[1])
        magnitude = math.sqrt((displacement[0] ** 2) + (displacement[1] ** 2))
        self.velocity = ((displacement[0] / magnitude) * speed, (displacement[1] / magnitude) * speed)

    def move(self):
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

    def kill(self):
        """
        Deletes the spark from the spark list
        """
        Spark.instances.remove(self)

    def draw(self):
        """
        Draws the spark onto the display
        """
        vertices = (
            self.pos,
            (self.pos[0] + self.velocity[0] * 2, self.pos[0] + self.velocity[0] * 2),
            (self.pos[0] + self.velocity[0] * 4, self.pos[1] + self.velocity[1] * 4),
            (self.pos[0] + self.velocity[0] * 2, self.pos[0] - self.velocity[0] * 2)
        )
        
        pygame.draw.polygon(self.game.display, (255, 255, 255), vertices)

class Game:
    def __init__(self):
        pygame.init()
        self.kill_screen = False
        pygame.display.set_caption("Treasure Trove")
        self.window = pygame.display.set_mode((426, 240))
        self.display = pygame.Surface((426, 240))
        self.clock = pygame.time.Clock()

        self.mouse_clicked = False
        self.spark_timer = 0

    def handle_events(self):
        """
        Handles all pygame events such as button presses
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.kill_screen = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.kill_screen = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_clicked = True

            if event.type == pygame.MOUSEBUTTONUP:
                self.mouse_clicked = False


    def update_display(self):
        """
        Calls all functions to update the display
        """
        self.display.fill((0, 0, 0))

        Spark.update()


        self.window.blit(pygame.transform.scale(self.display, self.window.get_size()), (0, 0))
        pygame.display.update()

    def run(self):
        """
        Runs the game loop
        """
        while not self.kill_screen:

            self.spark_timer = max(0, self.spark_timer - 1)

            if self.spark_timer <= 0 and self.mouse_clicked:
                mouse_pos = pygame.mouse.get_pos()
                Spark(self, (mouse_pos[0] - 1, mouse_pos[0] + 1), mouse_pos, 4)

            self.handle_events()
            self.update_display()
            self.clock.tick(60)


game = Game()
game.run()
pygame.quit()