import pygame, sys
from misc import get_text_surf, get_mouse_pos, update_options
from variables import *

class OptionsMenu:
    def __init__(self, window, fps):
        """
        Creates all the starting menu variables
        """
        # Display variables
        self.screentype = "options menu"
        self.selected_screen = "options menu"
        self.window = window
        self.user_resolution = (window.get_width(), window.get_height())

        # Player Variables
        self.fps = fps
        self.clicked = False
        self.mouse_pos = get_mouse_pos(self.user_resolution, GAME_RESOLUTION)

        # List of buttons [title, text on button, button rect]
        self.buttons = [
            ["Change Resolution", "<", (1220, 400, 100, 100), "decrease resolution"],
            ["", ">", (1620, 400, 100, 100), "increase resolution"], 
            ["Change FPS (Recommended 60)", "<", (1220, 600, 100, 100), "decrease fps"],
            ["", ">", (1620, 600, 100, 100), "increase fps"], 
            ["", "Return to Main Menu", ((GAME_RESOLUTION[0] // 2) - 300, 880, 600, 100), "main menu"]
            ]
        self.selected = None

        # Creates a rect for each button and adds it to the button's 2d list
        for i in range(len(self.buttons)):
            self.buttons[i][0] = get_text_surf(size=60, text=self.buttons[i][0], colour=pygame.Color("white"))

            self.buttons[i][1] = get_text_surf(size=60, text=self.buttons[i][1], colour=pygame.Color("white"))

            rect = pygame.Rect(self.buttons[i][2])
            self.buttons[i][2] = rect

        self.title_text = get_text_surf(size=100, text="Option Menu", colour=PRIMARY_COLOUR)

    def update_display(self):
        """
        Updates the screen
        """
        # Clears the screen
        SCREEN.fill((0, 0, 0))

        SCREEN.blit(self.title_text, ((GAME_RESOLUTION[0] // 2) - (self.title_text.get_width() // 2), 100))

        # Draws the buttons onto the screen
        for i, button in enumerate(self.buttons):
            if self.selected == i:
                pygame.draw.rect(SCREEN, PRIMARY_COLOUR, button[2])
            else:
                pygame.draw.rect(SCREEN, (255, 0, 0), button[2])

            # Draws the title for the button
            SCREEN.blit(button[0], (100, button[2].centery - (button[0].get_height() // 2)))
            # Draws the text onto the button
            SCREEN.blit(button[1], (button[2].centerx - (button[1].get_width() // 2), button[2].centery - (button[1].get_height() // 2)))

        # Shows the current resolution between the resolution buttons
        resolution_text = get_text_surf(size=55, text=f"{self.user_resolution[0]}x{self.user_resolution[1]}", colour=pygame.Color("white"))
        SCREEN.blit(resolution_text, (1470 - (resolution_text.get_width() // 2), 450 - (resolution_text.get_height() // 2)))

        # Shows the current fps between the fps buttons
        fps_text = get_text_surf(size=55, text=f"{self.fps} FPS", colour=pygame.Color("white"))
        SCREEN.blit(fps_text, (1470 - (fps_text.get_width() // 2), 650 - (fps_text.get_height() // 2)))

        # Draws the cursor on to the screen
        SCREEN.blit(CURSOR_1, self.mouse_pos) if self.clicked else SCREEN.blit(CURSOR_2, self.mouse_pos)

        #Shows the FPS
        fps_text = get_text_surf(size=55, text=f"FPS: {round(clock.get_fps())}", colour=pygame.Color("white"))
        SCREEN.blit(fps_text, (10, 10))

        # Ouputs the display in the user resolution
        self.window.blit(pygame.transform.scale(SCREEN, self.user_resolution), (0, 0))
        pygame.display.update()


    def handle_events(self):
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
                self.handle_buttons()

            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = get_mouse_pos(self.user_resolution, GAME_RESOLUTION)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
    def handle_buttons(self):
        """
        Checks which button has been pressed and runs the corresponding button
        """
        for button in self.buttons:
            if button[2].collidepoint(self.mouse_pos):
                if "resolution" in button[3]:
                    # Gets the next supported resolution
                    new_resolution = SUPPORTED_RESOLUTIONS[(SUPPORTED_RESOLUTIONS.index(self.user_resolution) + (-1 if button[3] == "increase resolution" else 1)) % len(SUPPORTED_RESOLUTIONS)]
                    # Quits the display and then recreates it with the new resolution
                    # This is necessary as pygame doesn't place the window in the centre unless I quit the display first
                    self.user_resolution = new_resolution
                    pygame.display.quit()
                    pygame.display.init()
                    self.window = pygame.display.set_mode(self.user_resolution)
                    pygame.mouse.set_visible(False)
                    pygame.display.set_caption("Treasure Trove")
                    pygame.display.set_icon(ICON_IMG)

                if "fps" in button[3]:
                    # Changes the resolution
                    self.fps = self.fps + (1 if button[3] == "increase fps" else -1)
                
                if button[3] == "main menu":
                    # Updates the options to save the new options
                    update_options(user_resolution=self.user_resolution, fps=self.fps)
                    # Changes the screen back to the main menu
                    self.selected_screen = "main menu"

    def run_frame(self):
        """
        Runs a frame of the menu
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


class CreditsMenu:
    def __init__(self, window, fps):
        """
        Creates all the starting menu variables
        """
        # Display Variables
        self.screentype = "credits menu"
        self.selected_screen = "credits menu"
        self.window = window
        self.user_resolution = (window.get_width(), window.get_height())

        # Player Variables
        self.fps = fps
        self.clicked = False
        self.mouse_pos = get_mouse_pos(self.user_resolution, GAME_RESOLUTION)

        # List of buttons [title, text on button, button rect]
        self.menu_button = [
            get_text_surf(size=60, text="Return to Main Menu", colour=pygame.Color("white")),
            pygame.Rect(((GAME_RESOLUTION[0] // 2) - 300, 880, 600, 100))
            ]
        self.selected = False

        self.credits = ["Developed by: Muhammad-Ali Mohsin", "Player Animation: https://game-endeavor.itch.io/mystic-woods", "Font: https://tinyworlds.itch.io/free-pixel-font-thaleah"]
        for i in range(len(self.credits)):
            self.credits[i] = get_text_surf(size=40, text=self.credits[i], colour=pygame.Color("white"))

        self.title_text = get_text_surf(size=100, text="Credits Menu", colour=PRIMARY_COLOUR)

    def update_display(self):
        """
        Updates the screen
        """
        # Clears the screen
        SCREEN.fill((0, 0, 0))

        SCREEN.blit(self.title_text, ((GAME_RESOLUTION[0] // 2) - (self.title_text.get_width() // 2), 100))

        # Draws the buttons onto the screen
        if self.selected:
            pygame.draw.rect(SCREEN, PRIMARY_COLOUR, self.menu_button[1])
        else:
            pygame.draw.rect(SCREEN, (255, 0, 0), self.menu_button[1])

        # Draws the text onto the button
        SCREEN.blit(self.menu_button[0], (self.menu_button[1].centerx - (self.menu_button[0].get_width() // 2), self.menu_button[1].centery - (self.menu_button[0].get_height() // 2)))

        for i in range(len(self.credits)):
            SCREEN.blit(self.credits[i], (100, (i * 100) + 400))

        # Draws the cursor on to the screen
        SCREEN.blit(CURSOR_1, self.mouse_pos) if self.clicked else SCREEN.blit(CURSOR_2, self.mouse_pos)

        #Shows the FPS
        fps_text = get_text_surf(size=55, text=f"FPS: {round(clock.get_fps())}", colour=pygame.Color("white"))
        SCREEN.blit(fps_text, (10, 10))

        # Ouputs the display in the user resolution
        self.window.blit(pygame.transform.scale(SCREEN, self.user_resolution), (0, 0))
        pygame.display.update()

    def handle_events(self):
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
                # Checks whether the mouse has clicked the return to menu and if so, changes the selected screen
                if self.menu_button[1].collidepoint(self.mouse_pos):
                    self.selected_screen = "main menu"

            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = get_mouse_pos(self.user_resolution, GAME_RESOLUTION)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    def run_frame(self):
        """
        Runs a frame of the menu
        """
        # Checks whether the mouse is hovering over a button and selects it if so
        self.selected = False
        if self.menu_button[1].collidepoint(self.mouse_pos):
            self.selected = True

        # Calls functions
        self.handle_events()
        self.update_display()
        clock.tick(self.fps)

