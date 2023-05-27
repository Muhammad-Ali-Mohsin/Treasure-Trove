import pygame, sys
from misc import get_text_surf, get_mouse_pos
from variables import *


class MainMenu:
    def __init__(self):
        """
        Creates all the starting game variables
        """
        # Game Variables
        self.fps = FPS
        self.clicked = False
        self.mouse_pos = get_mouse_pos(USER_RESOLUTION, GAME_RESOLUTION)

        # List of buttons [button label, selected screen]
        self.buttons = [["Start Game", "game"], ["Options", "main menu"], ["Leaderboard", "main menu"], ["Credits", "main menu"], ["Exit to Desktop", "close"]]
        self.selected = None
        self.selected_screen = "main menu"

        # Creates a rect for each button and adds it to the button's 2d list
        for i in range(len(self.buttons)):
            rect = pygame.Rect((USER_RESOLUTION[0] // 2) - 300, ((i + 1) * 130) + 300, 600, 90)
            self.buttons[i].append(rect)



    def update_display(self):
        """
        Updates the screen
        """
        # Clears the screen
        SCREEN.fill((0, 0, 0))

        # Draws the buttons onto the screen
        for i, button in enumerate(self.buttons):
            if self.selected == i:
                pygame.draw.rect(SCREEN, (255, 0, 0), button[2])
            else:
                pygame.draw.rect(SCREEN, (255, 187, 0), button[2])

            # Draws the text onto the button
            button_label = get_text_surf(size=80, text=button[0], colour=pygame.Color("white"))
            SCREEN.blit(button_label, (button[2].centerx - (button_label.get_width() // 2), button[2].centery - (button_label.get_height() // 2)))

        # Draws the cursor on to the screen
        SCREEN.blit(CURSOR_1, self.mouse_pos) if self.clicked else SCREEN.blit(CURSOR_2, self.mouse_pos)

        #Shows the FPS
        fps_text = get_text_surf(size=55, text=f"FPS: {round(clock.get_fps())}", colour=pygame.Color("white"))
        SCREEN.blit(fps_text, (10, 10))

        # Ouputs the display in the user resolution
        WINDOW.blit(pygame.transform.scale(SCREEN, USER_RESOLUTION), (0, 0))
        pygame.display.update()


    def handle_events(self):
        global USER_RESOLUTION
        global WINDOW
        """
        Handles all input events such as key presses
        """
        for event in pygame.event.get():
            # Checks whether the X button has been pressed
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: self.clicked = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: self.clicked = False
                # Checks whether the mouse has clicked a button and if so, changes the selected screen
                for button in self.buttons:
                    if button[2].collidepoint(self.mouse_pos):
                        self.selected_screen = button[1]

            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = get_mouse_pos(USER_RESOLUTION, GAME_RESOLUTION)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    def loop(self):
        """
        The game loop
        """

        # Checks whether the mouse is hovering over a button and selects it if so
        self.selected = None
        for i, button in enumerate(self.buttons):
            if button[2].collidepoint(self.mouse_pos):
                self.selected = i

        # Calls functions
        self.handle_events()
        self.update_display()
        clock.tick(self.fps)

