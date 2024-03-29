import math

import pygame

from scripts.utils import get_text_surf, format_num

class HUD:
    def __init__(self, game):
        self.game = game
        self.compass_angle = 0
        self.text_updated = False
        self.text = {
            'paused': get_text_surf(size=70, text="Paused", colour=(172, 116, 27)), 
            'game_over': get_text_surf(size=70, text="Game Over", colour=(172, 116, 27)),
            'return': get_text_surf(size=20, text="Press Backspace to return to Main Menu", colour=(172, 116, 27)),
            'wave_label': get_text_surf(size=30, text=f"Wave:", colour=(172, 116, 27)),
            'killed_label': get_text_surf(size=30, text=f"Enemies Killed:", colour=(172, 116, 27)),
            'remaining_label': get_text_surf(size=30, text=f"Enemies Remaining:", colour=(172, 116, 27)),
            'gold_label': get_text_surf(size=30, text=f"Gold collected:", colour=(172, 116, 27))
            }

    def update(self):
        # Updates the text if the game is over or paused and hasn't been updated
        if (self.game.game_over or self.game.paused) and not self.text_updated:
            self.update_text()
            self.text_updated = True
        else:
            # Sets the updated flag to false if the game is not over or paused
            self.text_updated = False

        if self.game.game_over:
            self.draw_screen(self.text['game_over'])
        elif self.game.paused:
            self.draw_screen(self.text['paused'])

        self.draw_healthbar()
        self.draw_gold()
        self.draw_compass()
        self.draw_special_attacks()

    def draw_compass(self):
        """
        Draws the compass
        """
        # Retrieves the player location and calculates the displacement from the player to the treasure
        player_loc = self.game.maze.get_loc(self.game.player.get_center())
        displacement = (self.game.treasure.loc[0] - player_loc[0], self.game.treasure.loc[1] - player_loc[1])

        # Spins the compass around if the player is standing over the treasure
        if player_loc == self.game.treasure.loc:
            angle = (self.compass_angle + round(10 * self.game.multi)) % 360
        else:
            angle = (math.degrees(math.atan2(displacement[1], displacement[0])) + 360) % 360
            
        self.compass_angle = angle
        self.game.larger_display.blit(self.game.images['compass_base'], (self.game.larger_display.get_width() - self.game.images['compass_base'].get_width() - 30, 30))
        # Rotates the spinner image by the angle towards treasure and subtracts 45 from angle as the spinner is already rotated 45 degrees clockwise in the image
        # Angle is also made negative because pygame rotates images anticlockwise and I want to rotate clockwise
        spinner_img = pygame.transform.rotate(self.game.images['compass_spinner'], -angle - 45)
        # Draws the spinner image at the centre of the compass image
        pos = (self.game.larger_display.get_width() - (self.game.images['compass_base'].get_width() // 2) - (spinner_img.get_width() // 2) - 30, (self.game.images['compass_base'].get_height() // 2) - (spinner_img.get_height() // 2) + 30)
        self.game.larger_display.blit(spinner_img, pos)


    def draw_healthbar(self):
        """
        Draws the healthbar image as as well as the player's health
        """
        # Draws a red rect to represent te health and then the healthbar image on top
        pygame.draw.rect(self.game.larger_display, (255, 0, 0), (84, 42, (self.game.player.health / 100) * 231, 18))
        self.game.larger_display.blit(self.game.images['healthbar'], (15, 15))

    def draw_gold(self):
        """
        Draws the player's gold onto the screen
        """
        gold_text = get_text_surf(size=45, text=f"{format_num(self.game.gold)} gold", colour=(255, 202, 24))
        self.game.larger_display.blit(self.game.images['gold_pouch'], (15, 105))
        self.game.larger_display.blit(gold_text, (self.game.images['gold_pouch'].get_width() + 30, 96 + (gold_text.get_height() // 2)))

    def draw_special_attacks(self):
        """
        Draws the special attack icons on to the screen
        """
        x = 25
        for i, icon in enumerate(('dash_icon', 'spiral_icon', 'explode_icon')):
            self.game.larger_display.blit(self.game.images[icon], (x, self.game.larger_display.get_height() - 25 - self.game.images[icon].get_height()))
            self.game.larger_display.blit(self.game.number_images[self.game.special_attacks[i]], (x + 77 - self.game.number_images[self.game.special_attacks[i]].get_width() // 2, self.game.larger_display.get_height() - 25 - self.game.images[icon].get_height()))
            x += 15 + self.game.images[icon].get_width()

    def draw_screen(self, text):
        """
        Draws a screen with a given text as the center (Used for the pause screen and game over screen)
        """
        # Draws the grey screen, the box, the return to menu text and the title text
        self.game.display.blit(self.game.images['grey_screen'], (0, 0))
        box_pos = ((self.game.larger_display.get_width() // 2) - (self.game.images['box'].get_width() // 2), (self.game.larger_display.get_height() // 2) - (self.game.images['box'].get_height() // 2))
        self.game.larger_display.blit(self.game.images['box'], box_pos)
        self.game.larger_display.blit(text, ((self.game.larger_display.get_width() // 2) - (text.get_width() // 2), (self.game.larger_display.get_height() // 2) - (text.get_height() // 2) - 80))
        self.game.larger_display.blit(self.text['return'], ((self.game.larger_display.get_width() // 2) - (self.text['return'].get_width() // 2), (self.game.larger_display.get_height() // 2) - (self.text['return'].get_height() // 2) + 120))

        # Draws the metrics onto the screen
        for i, metric in enumerate(('wave', 'killed', 'remaining', 'gold')):
            self.game.larger_display.blit(self.text[metric + '_label'], (box_pos[0] + 100, (self.game.larger_display.get_height() // 2) - (self.text[metric + '_label'].get_height() // 2) + (i * 30) - 20))
            self.game.larger_display.blit(self.text[metric], (box_pos[0] + self.game.images['box'].get_width() - (self.text[metric].get_width() // 2) - 100, (self.game.larger_display.get_height() // 2) - (self.text[metric].get_height() // 2) + (i * 30) - 20))

    def update_text(self):
        """
        Updates the text surfaces that are drawn during the pause and game over screens
        """
        self.text['wave'] = get_text_surf(size=30, text=str(self.game.wave), colour=(172, 116, 27))
        self.text['killed'] = get_text_surf(size=30, text=str(self.game.killed), colour=(172, 116, 27))
        self.text['remaining'] = get_text_surf(size=30, text=str(len(self.game.enemies)), colour=(172, 116, 27))
        self.text['gold'] = get_text_surf(size=30, text=format_num(self.game.gold), colour=(172, 116, 27))