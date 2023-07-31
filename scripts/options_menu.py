import pygame

from scripts.utils import load_image, get_text_surf, scale_coord_to_new_res

RESOLUTIONS = ((3840, 2160), (2560, 1440), (1920, 1080), (1280, 720), (854, 480), (640, 360), (426, 240))

class OptionsMenu:
    def __init__(self, window, fps):
        self.kill_screen = False
        self.fps = fps
        self.window = window
        pygame.display.set_caption("Treasure Trove - Options Menu")
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
        self.selected = None

        self.buttons = [
            {'label': get_text_surf(size=60, text="<", colour=(255, 255, 255)), 'action': 'decrease_res', 'rect': pygame.Rect((800, 250, 75, 75))},
            {'label': get_text_surf(size=60, text=">", colour=(255, 255, 255)), 'action': 'increase_res', 'rect': pygame.Rect((1100, 250, 75, 75))},
            {'label': get_text_surf(size=60, text="<", colour=(255, 255, 255)), 'action': 'decrease_fps', 'rect': pygame.Rect((800, 350, 75, 75))},
            {'label': get_text_surf(size=60, text=">", colour=(255, 255, 255)), 'action': 'increase_fps', 'rect': pygame.Rect((1100, 350, 75, 75))},
            {'label': get_text_surf(size=40, text="Return to Main Menu", colour=(255, 255, 255)), 'action': 'main_menu', 'rect': pygame.Rect(((self.display.get_width() // 2) - 200, self.display.get_height() - 125, 400, 50))}
        ]

        self.text = [
            {'text': get_text_surf(size=70, text="Options Menu", colour=(255, 202, 24)), 'pos': None},
            {'text': get_text_surf(size=40, text="Change Resolution", colour=(255, 255, 255)), 'pos': None},
            {'text': get_text_surf(size=40, text="Change FPS", colour=(255, 255, 255)), 'pos': None},
            {'text': get_text_surf(size=40, text=f"{self.window.get_width()}x{self.window.get_height()}", colour=(255, 255, 255)), 'pos': (100, 250)},
            {'text': get_text_surf(size=40, text=str(self.fps), colour=(255, 255, 255)), 'pos': (100, 350)}
        ]

        self.text[0]['pos'] = ((self.display.get_width() // 2) - (self.text[0]['text'].get_width() // 2), 50)
        self.text[1]['pos'] = (100, 250 + (self.text[1]['text'].get_height() // 2))
        self.text[2]['pos'] = (100, 350 + (self.text[2]['text'].get_height() // 2))
        self.text[3]['pos'] = (990 - (self.text[3]['text'].get_width() // 2), 250 + (self.text[3]['text'].get_height() // 2))
        self.text[4]['pos'] = (990 - (self.text[4]['text'].get_width() // 2), 350 + (self.text[4]['text'].get_height() // 2))

    def update_display(self):
        """
        Updates the screen
        """
        # Clears the screen
        self.display.fill((0, 0, 0))

        # Draws the text onto the screen
        for text in self.text:
            self.display.blit(text['text'], text['pos'])

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
                        self.button_press(button)
                        break

            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = scale_coord_to_new_res(pygame.mouse.get_pos(), self.window.get_size(), self.display.get_size())
                self.selected = None
                for i, button in enumerate(self.buttons):
                    if button['rect'].collidepoint(self.mouse_pos): 
                        self.selected = i

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.kill_screen = True

    def button_press(self, button):
        if "fps" in button['action']:
            self.fps += 1 if button['action'] == "increase_fps" else -1
            self.text[4]['text'] = get_text_surf(size=40, text=str(self.fps), colour=(255, 255, 255))

        elif "res" in button['action']:
            new_res = RESOLUTIONS[(RESOLUTIONS.index(self.window.get_size()) + (1 if button['action'] == "decrease_res" else -1)) % len(RESOLUTIONS)]
            pygame.display.quit()
            pygame.display.init()
            self.window = pygame.display.set_mode(new_res)
            pygame.mouse.set_visible(False)
            pygame.display.set_caption("Treasure Trove - Options Menu")
            pygame.display.set_icon(load_image("assets/images/icon.png"))
            self.text[3]['text'] = get_text_surf(size=40, text=f"{self.window.get_width()}x{self.window.get_height()}", colour=(255, 255, 255))

        elif button['action'] == "main_menu":
            self.selected_screen = "main_menu"
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