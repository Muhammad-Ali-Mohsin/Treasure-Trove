import pygame

from scripts.utils import load_image, scale_coord_to_new_res, get_text_surf, create_window, load_high_scores, AudioPlayer

RESOLUTIONS = ((3840, 2160), (2560, 1440), (1920, 1080), (1280, 720), (854, 480), (640, 360), (426, 240))

class Menu:
    def __init__(self, window, fps):
        # Display variables
        self.kill_screen = False
        self.fps = fps
        self.window = window
        self.display = pygame.Surface((1280, 720))
        self.clock = pygame.time.Clock()
        
        # Menu variables
        self.images = {
            'cursor_0': load_image("assets/images/cursor_0.png"),
            'cursor_1': load_image("assets/images/cursor_1.png")
        }
        self.buttons = []
        self.text = []

        # Player Variables
        self.clicked = False
        self.mouse_pos = scale_coord_to_new_res(pygame.mouse.get_pos(), self.window.get_size(), self.display.get_size())
        self.selected_screen = None
        self.selected = None

        # Audio
        self.music = pygame.mixer.Sound("assets/sfx/menu_music.wav")
        self.music.set_volume(0.5)
        self.music.play(-1, fade_ms=1000)
        AudioPlayer.load_sound("hover", "assets/sfx/hover.wav", 0.5)
        AudioPlayer.load_sound("click", "assets/sfx/click.wav", 1)

    def update_display(self):
        """
        Updates the screen
        """
        # Clears the screen
        self.display.fill((0, 0, 0))

        # Draws the text onto the screen
        for text in self.text:
            self.display.blit(text['surf'], text['pos'])

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
            if event.type == pygame.QUIT:
                self.kill_screen = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.clicked = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.clicked = False
                    for button in self.buttons:
                        if button['rect'].collidepoint(self.mouse_pos):
                            self.button_press(button)
                            break

            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = scale_coord_to_new_res(pygame.mouse.get_pos(), self.window.get_size(), self.display.get_size())
                selected = None
                for i, button in enumerate(self.buttons):
                    if button['rect'].collidepoint(self.mouse_pos): 
                        if i != self.selected:
                            AudioPlayer.play_sound("hover")
                        selected = i
                        break
                self.selected = selected

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.kill_screen = True

    def button_press(self, button):
        """
        Runs whenever a button is pressed
        """
        AudioPlayer.play_sound("click")

    def run(self):
        """
        Runs a frame of the main menu
        """
        while not self.kill_screen:

            # Calls functions
            self.handle_events()
            self.update_display()
            self.clock.tick(self.fps)

        self.music.stop()
        return self.selected_screen
    

class MainMenu(Menu):
    def __init__(self, window, fps):
        super().__init__(window, fps)
        pygame.display.set_caption("Treasure Trove - Main Menu")

        #Loads all the buttons in
        self.buttons = []
        for i, data in enumerate((("Start Game", "game"), ("Options", "options_menu"), ("Leaderboard", "leaderboard"), ("Credits", "credits_menu"), ("Exit to Desktop", None))):
            self.buttons.append({
                'label': get_text_surf(size=40, text=data[0], colour=(255, 255, 255)), 
                'action': data[1],
                'rect': pygame.Rect((self.display.get_width() // 2) - 150, ((i + 1) * 50) + 300, 300, 40)
                })

        self.text = [
            {'surf': get_text_surf(size=100, text="Treasure Trove", colour=(255, 202, 24)), 'pos': None},
        ]

        self.text[0]['pos'] = ((self.display.get_width() // 2) - (self.text[0]['surf'].get_width() // 2), 100)

    def button_press(self, button):
        super().button_press(button)
        self.selected_screen = button['action']
        self.kill_screen = True


class OptionsMenu(Menu):
    def __init__(self, window, fps):
        super().__init__(window, fps)
        pygame.display.set_caption("Treasure Trove - Options")

        self.buttons = [
            {'label': get_text_surf(size=60, text="<", colour=(255, 255, 255)), 'action': 'decrease_res', 'rect': pygame.Rect((800, 250, 75, 75))},
            {'label': get_text_surf(size=60, text=">", colour=(255, 255, 255)), 'action': 'increase_res', 'rect': pygame.Rect((1100, 250, 75, 75))},
            {'label': get_text_surf(size=60, text="<", colour=(255, 255, 255)), 'action': 'decrease_fps', 'rect': pygame.Rect((800, 350, 75, 75))},
            {'label': get_text_surf(size=60, text=">", colour=(255, 255, 255)), 'action': 'increase_fps', 'rect': pygame.Rect((1100, 350, 75, 75))},
            {'label': get_text_surf(size=40, text="Return to Main Menu", colour=(255, 255, 255)), 'action': 'main_menu', 'rect': pygame.Rect(((self.display.get_width() // 2) - 200, self.display.get_height() - 125, 400, 50))}
        ]

        self.text = [
            {'surf': get_text_surf(size=70, text="Options Menu", colour=(255, 202, 24)), 'pos': None},
            {'surf': get_text_surf(size=40, text="Change Resolution", colour=(255, 255, 255)), 'pos': None},
            {'surf': get_text_surf(size=40, text="Change FPS", colour=(255, 255, 255)), 'pos': None},
            {'surf': get_text_surf(size=40, text=f"{self.window.get_width()}x{self.window.get_height()}", colour=(255, 255, 255)), 'pos': (100, 250)},
            {'surf': get_text_surf(size=40, text=str(self.fps), colour=(255, 255, 255)), 'pos': (100, 350)}
        ]

        self.text[0]['pos'] = ((self.display.get_width() // 2) - (self.text[0]['surf'].get_width() // 2), 50)
        self.text[1]['pos'] = (100, 250 + (self.text[1]['surf'].get_height() // 2))
        self.text[2]['pos'] = (100, 350 + (self.text[2]['surf'].get_height() // 2))
        self.text[3]['pos'] = (990 - (self.text[3]['surf'].get_width() // 2), 250 + (self.text[3]['surf'].get_height() // 2))
        self.text[4]['pos'] = (990 - (self.text[4]['surf'].get_width() // 2), 350 + (self.text[4]['surf'].get_height() // 2))

    def button_press(self, button):
        super().button_press(button)
        if "fps" in button['action']:
            self.fps += 1 if button['action'] == "increase_fps" else -1
            self.text[4]['surf'] = get_text_surf(size=40, text=str(self.fps), colour=(255, 255, 255))

        elif "res" in button['action']:
            new_res = RESOLUTIONS[(RESOLUTIONS.index(self.window.get_size()) + (1 if button['action'] == "decrease_res" else -1)) % len(RESOLUTIONS)]
            pygame.display.quit()
            self.window = create_window(new_res)
            pygame.display.set_caption("Treasure Trove - Options Menu")
            self.text[3]['surf'] = get_text_surf(size=40, text=f"{self.window.get_width()}x{self.window.get_height()}", colour=(255, 255, 255))

        elif button['action'] == "main_menu":
            self.selected_screen = "main_menu"
            self.kill_screen = True


class CreditsMenu(Menu):
    def __init__(self, window, fps):
        super().__init__(window, fps)
        pygame.display.set_caption("Treasure Trove - Credits")

        self.buttons = [{'label': get_text_surf(size=40, text="Return to Main Menu", colour=(255, 255, 255)), 'action': 'main_menu', 'rect': pygame.Rect(((self.display.get_width() // 2) - 200, self.display.get_height() - 125, 400, 50))}]

        self.text = [{'surf': get_text_surf(size=70, text="Credits", colour=(255, 202, 24)), 'pos': None}]
        self.text[0]['pos'] = ((self.display.get_width() // 2) - (self.text[0]['surf'].get_width() // 2), 50)

        credits = [
            "|Created by: Muhammad-Ali Mohsin", 
            "",
            "|Programming, Artwork and Design",
            "  Muhammad-Ali Mohsin",
            "",
            "|Free assets used",
            "Player and Enemy animations",
            "https://game-endeavor.itch.io/mystic-woods",
            "",
            "Font",
            "https://tinyworlds.itch.io/free-pixel-font-thaleah",
            "",
            "Sound effects:",
            "https://opengameart.org/content/forest-ambience",
            "https://opengameart.org/content/sleep-talking-loop-fantasy-rpg-sci-fi",
            "https://opengameart.org/content/fantozzis-footsteps-grasssand-stone",
            "https://leohpaz.itch.io/rpg-essentials-sfx-free",
            "https://opengameart.org/content/sack-of-gold",
            "https://opengameart.org/content/menu-music",
            "https://opengameart.org/content/game-over-bad-chest-sfx"
            ]

        for i, text in enumerate(credits):
            if text == "":
                colour = (0, 0, 0)
            elif text[:5] == "https":
                colour = (176, 176, 176)
            elif text[0] == "|":
                text = text[1:]
                colour = (58, 148, 186)
            else:
                colour = (255, 255, 255)
            surf = get_text_surf(size=20, text=text, colour=colour)
            self.text.append({
                'surf': surf, 
                'pos': ((self.display.get_width() // 2) - (surf.get_width() // 2), 150 + (i * 20))
                })

    def button_press(self, button):
        super().button_press(button)
        if button['action'] == "main_menu":
            self.selected_screen = "main_menu"
            self.kill_screen = True


class LeaderboardMenu(Menu):
    def __init__(self, window, fps):
        super().__init__(window, fps)
        pygame.display.set_caption("Treasure Trove - Leaderboard")

        self.buttons = [{'label': get_text_surf(size=40, text="Return to Main Menu", colour=(255, 255, 255)), 'action': 'main_menu', 'rect': pygame.Rect(((self.display.get_width() // 2) - 200, self.display.get_height() - 125, 400, 50))}]

        self.text = [{'surf': get_text_surf(size=70, text="Leaderboard", colour=(255, 202, 24)), 'pos': None}]
        self.text[0]['pos'] = ((self.display.get_width() // 2) - (self.text[0]['surf'].get_width() // 2), 50)

        high_scores = load_high_scores()

        for i, score in enumerate(high_scores):
            surf = get_text_surf(size=35, text=f"{i + 1}) {score[0]} - {score[1]}", colour=(255, 255, 255))
            self.text.append({
                'surf': surf, 
                'pos': ((self.display.get_width() // 2) - (surf.get_width() // 2), 200 + (i * 30))
                })

    def button_press(self, button):
        super().button_press(button)
        if button['action'] == "main_menu":
            self.selected_screen = "main_menu"
            self.kill_screen = True