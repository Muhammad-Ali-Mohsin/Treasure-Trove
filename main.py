import pygame
pygame.init()
from variables import ICON_IMG
from game import Game
from main_menu import MainMenu

# Set up pygame
pygame.mouse.set_visible(False)
pygame.display.set_caption("Treasure Trove")
pygame.display.set_icon(ICON_IMG)

selected_screen = "main menu"

while True:
    if selected_screen == "main menu":
        # Creates a main menu and runs it until the selected screen has been changed
        main_menu = MainMenu()
        while main_menu.selected_screen == "main menu":
            main_menu.loop()
        selected_screen = main_menu.selected_screen
    
    if selected_screen == "game":
        # Creates the game and runs it until the game is over and then returns to the main menu
        game = Game()
        while game.game_over == False:
            game.loop()
        selected_screen = "main menu"

    if selected_screen == "close":
        # Exits the game
        pygame.display.quit()
        break