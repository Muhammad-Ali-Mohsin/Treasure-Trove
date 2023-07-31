import pygame

from scripts.utils import load_image, get_text_surf, scale_coord_to_new_res

class MainMenu:
    def __init__(self, window, fps):
        self.kill_screen = False
        self.fps = fps
        self.window = window
        pygame.display.set_caption("Treasure Trove - Main Menu")
        self.display = pygame.Surface((1280, 720))
        self.clock = pygame.time.Clock()
        
        self.images = {
            'cursor_0': load_image("assets/images/cursor_0.png"),
            'cursor_1': load_image("assets/images/cursor_1.png")
        }

        # Player Variables
        self.clicked = False
        self.mouse_pos = pygame.mouse.get_pos()
        self.selected_screen = None

        self.buttons = []
        self.selected = None

        for i, data in enumerate((("Start Game", "game"), ("Options", "options_menu"), ("Leaderboard", "main_menu"), ("Credits", "credits_menu"), ("Exit to Desktop", None))):
            self.buttons.append({
                'label': get_text_surf(size=40, text=data[0], colour=pygame.Color("white")), 
                'action': data[1],
                'rect': pygame.Rect((self.display.get_width() // 2) - 150, ((i + 1) * 50) + 300, 300, 40)
                })

        self.title_text = get_text_surf(size=100, text="Treasure Trove", colour=(255, 202, 24))

    def update_display(self):
        """
        Updates the screen
        """
        # Clears the screen
        self.display.fill((0, 0, 0))

        # Blits the title
        self.display.blit(self.title_text, ((self.display.get_width() // 2) - (self.title_text.get_width() // 2), 100))

        # Draws the buttons onto the screen
        for i, button in enumerate(self.buttons):
            pygame.draw.rect(self.display, (255, 202, 24) if self.selected == i else (255, 0, 0), button['rect'])
            self.display.blit(button['label'], (button['rect'].centerx - (button['label'].get_width() // 2), button['rect'].centery - (button['label'].get_height() // 2)))

        # Draws the cursor on to the screen
        self.display.blit(self.images['cursor_0'] if self.clicked else self.images['cursor_1'], self.mouse_pos)

        # Ouputs the display in the user resolution
        self.window.blit(pygame.transform.scale(self.display, self.window.get_size()), (0, 0))
        pygame.display.update()

    def handle_events(self):
        """
        Handles all input events such as key presses
        """
        for event in pygame.event.get():
            # Checks whether the X button has been pressed
            if event.type == pygame.QUIT:
                self.kill_screen = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: self.clicked = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: self.clicked = False
                # Checks whether the mouse has clicked a button and if so, changes the selected screen
                for button in self.buttons:
                    if button['rect'].collidepoint(self.mouse_pos):
                        self.selected_screen = button['action']
                        self.kill_screen = True

            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = scale_coord_to_new_res(pygame.mouse.get_pos(), self.window.get_size(), self.display.get_size())
                self.selected = None
                for i, button in enumerate(self.buttons):
                    if button['rect'].collidepoint(self.mouse_pos): 
                        self.selected = i

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.kill_screen = True

    def run(self):
        """
        Runs a frame of the main menu
        """
        while not self.kill_screen:

            # Calls functions
            self.handle_events()
            self.update_display()
            self.clock.tick(self.fps)

        return self.selected_screen