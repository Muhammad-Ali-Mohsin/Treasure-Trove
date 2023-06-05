import pygame, math
from variables import COMPASS_BASE_IMG, COMPASS_SPINNER_IMG, GAME_RESOLUTION, SCREEN

class Compass:
    def __init__(self):
        self.angle = 0

    def calculate_angle(self, player_location, treasure_location, dt):
        """
        Calculates the angle that the spinner needs to be rotated by to point to the treasure
        """
        # Checks if the player is standing on the treasure and makes the compass spin if they are
        if player_location == treasure_location:
            self.angle = (self.angle + round(400 * dt)) % 360
        else:
            x = player_location[0] - treasure_location[0]
            y = player_location[1] - treasure_location[1]

            # Calculates the angle if the x or y coordinates are the same because a triangle can't be formed in that case as the displacement is a horizontal or vertical line
            if x == 0:
                self.angle = 180 if y < 0 else 0
            elif y == 0:
                self.angle = 90 if x < 0 else 270
            else:
                # Calculates the angle in radians using inverse tan and then converts to degrees
                self.angle = math.degrees(math.atan(abs(y) / abs(x)))

                if x > 0: # This means the player is to the right of the treasure
                    if y > 0: # This means the player is below the treasure
                        self.angle = 270 + self.angle
                    else: # This means the player is above the treasure
                        self.angle = 270 - self.angle
                else: # This means the player is to the left of the treasure
                    if y > 0: # This means the player is below the treasure
                        self.angle = 90 - self.angle
                    else: # This means the player is above the treasure
                        self.angle = 90 + self.angle

    def draw(self):
        """
        Draws the compass onto the screen
        """
        # Draws the base image
        SCREEN.blit(COMPASS_BASE_IMG, (GAME_RESOLUTION[0] - COMPASS_BASE_IMG.get_width() - 20, 20))
        # Rotates the spinner image by the angle towards treasure and subtracts 45 from angle as compass image is already rotated 45 degrees clockwise
        # Angle is also made negative because pygame rotates images anticlockwise and I want to rotate clockwise
        spinner_img = pygame.transform.rotate(COMPASS_SPINNER_IMG, -self.angle + 45)
        # Draws the spinner image at the centre of the compass image
        pos = (GAME_RESOLUTION[0] - (COMPASS_BASE_IMG.get_width() // 2) - (spinner_img.get_width() // 2) - 20, (COMPASS_BASE_IMG.get_height() // 2) - (spinner_img.get_height() // 2) + 20)
        SCREEN.blit(spinner_img, pos)
