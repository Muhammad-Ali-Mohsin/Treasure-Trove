import math

import pygame

PADDING = 30

class Compass:
    def __init__(self, game):
        self.game = game
        self.angle = 0

    def update(self):
        """
        Calculates the angle that the spinner needs to be rotated by to point to the treasure
        """
        player_loc = self.game.maze.get_loc(self.game.player.get_center())
        displacement = (player_loc[0] - self.game.treasure.loc[0], player_loc[1] - self.game.treasure.loc[1])

        if player_loc == self.game.treasure.loc:
            angle = (self.angle + round(10 * self.game.multi)) % 360
        elif displacement[0] == 0:
            angle = 180 if displacement[1] < 0 else 0
        elif displacement[1] == 0:
            angle = 90 if displacement[0] < 0 else 270
        else:
            # Calculates the angle in radians using inverse tan and then converts to degrees
            angle = math.degrees(math.atan(abs(displacement[1] / displacement[0])))

            if displacement[0] > 0: # This means the player is to the right of the treasure
                if displacement[1] > 0: # This means the player is below the treasure
                    angle = 270 + angle
                else: # This means the player is above the treasure
                    angle = 270 - angle
            else: # This means the player is to the left of the treasure
                if displacement[1] > 0: # This means the player is below the treasure
                    angle = 90 - angle
                else: # This means the player is above the treasure
                    angle = 90 + angle

        self.angle = angle

    def draw(self):
        """
        Draws the compass onto the screen
        """
        self.game.larger_display.blit(self.game.images['compass_base'], (self.game.larger_display.get_width() - self.game.images['compass_base'].get_width() - PADDING, PADDING))
        # Rotates the spinner image by the angle towards treasure and subtracts 45 from angle as the spinner is already rotated 45 degrees clockwise in the image
        # Angle is also made negative because pygame rotates images anticlockwise and I want to rotate clockwise
        spinner_img = pygame.transform.rotate(self.game.images['compass_spinner'], -self.angle + 45)
        # Draws the spinner image at the centre of the compass image
        pos = (self.game.larger_display.get_width() - (self.game.images['compass_base'].get_width() // 2) - (spinner_img.get_width() // 2) - PADDING, (self.game.images['compass_base'].get_height() // 2) - (spinner_img.get_height() // 2) + PADDING)
        self.game.larger_display.blit(spinner_img, pos)
