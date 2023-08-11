import time

import pygame

from scripts.utils import AudioPlayer, load_image, load_data, save_data, get_text_surf, get_hash, create_window, format_num, scale_coord_to_new_res

RESOLUTIONS = ((3840, 2160), (2560, 1440), (1920, 1080), (1280, 720), (854, 480), (640, 360), (426, 240))

class Menu:
    def __init__(self, window, fps):
        # Display variables
        self.kill_screen = False
        self.fps = fps
        self.window = window
        self.display = pygame.Surface((1280, 720))
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.last_time = time.time()
        
        # Menu variables
        self.images = {
            'cursor_0': load_image("assets/images/cursor_0.png"),
            'cursor_1': load_image("assets/images/cursor_1.png"),
        }
        self.buttons = {}
        self.textboxes = {}
        self.text = []
        self.error_msg = {'surf': None, 'pos': None}
        self.cursor_timer = 0

        # Player Variables
        self.clicked = False
        self.mouse_pos = scale_coord_to_new_res(pygame.mouse.get_pos(), self.window.get_size(), self.display.get_size())
        self.selected_screen = None
        self.selected = None
        self.selected_textbox = None

        # Loads the background music and ambience and plays it on a loop
        self.music = pygame.mixer.Sound("assets/sfx/menu_music.wav")
        self.music.set_volume(0.5)
        self.music.play(-1, fade_ms=1000)

        # Loads all the sound effects
        AudioPlayer.load_sound("hover", "assets/sfx/hover.wav", 0.5)
        AudioPlayer.load_sound("click", "assets/sfx/click.wav", 1)
        AudioPlayer.load_sound("error", "assets/sfx/error.wav", 1)

    def update_display(self):
        """
        Updates the screen
        """
        # Clears the screen
        if "bg" in self.images:
            self.display.blit(pygame.transform.scale(self.images['bg'], self.display.get_size()), (0, 0))
        else:
            self.display.fill((0, 0, 0))

        # Draws the text onto the screen
        for text in self.text:
            self.display.blit(text['surf'], text['pos'])

        # Draws the buttons onto the screen
        for _id in self.buttons:
            button = self.buttons[_id]
            pygame.draw.rect(self.display, (255, 202, 24) if self.selected == button['id'] else (255, 0, 0), button['rect'])
            self.display.blit(button['label'], (button['rect'].centerx - (button['label'].get_width() // 2), button['rect'].centery - (button['label'].get_height() // 2)))

        # Draws the textboxes onto the screen
        for _id in self.textboxes:
            textbox = self.textboxes[_id]
            pygame.draw.rect(self.display, (255, 0, 0), textbox['rect'])
            self.display.blit(textbox['text_surf'], (textbox['rect'].centerx - (textbox['text_surf'].get_width() // 2), textbox['rect'].centery - (textbox['text_surf'].get_height() // 2)))

        # Draws the error message
        if self.error_msg['surf'] != None:
            self.display.blit(self.error_msg['surf'], (self.error_msg['pos'][0] - self.error_msg['surf'].get_width() // 2, self.error_msg['pos'][1] - self.error_msg['surf'].get_height() // 2))

        # Draws the cursor on to the screen
        self.display.blit(self.images['cursor_0'] if self.clicked else self.images['cursor_1'], self.mouse_pos)

        # Draws the textbox cursor
        if self.selected_textbox != None and self.cursor_timer <= 0.5:
            textbox = self.selected_textbox
            pygame.draw.rect(self.display, (255, 255, 255), (textbox['rect'].centerx + (textbox['text_surf'].get_width() // 2) + 5, textbox['rect'].centery - 13, 3, 26))

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
                    self.selected_textbox = None
                    for _id in self.buttons:
                        if self.buttons[_id]['rect'].collidepoint(self.mouse_pos):
                            self.button_press(self.buttons[_id])
                            break

                    for _id in self.textboxes:
                        if self.textboxes[_id]['rect'].collidepoint(self.mouse_pos):
                            self.selected_textbox = self.textboxes[_id]
                            AudioPlayer.play_sound("click")
                            break

            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = scale_coord_to_new_res(pygame.mouse.get_pos(), self.window.get_size(), self.display.get_size())
                selected = None
                for _id in self.buttons:
                    if self.buttons[_id]['rect'].collidepoint(self.mouse_pos): 
                        if _id != self.selected:
                            AudioPlayer.play_sound("hover")
                        selected = _id
                        break
                self.selected = selected

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.kill_screen = True
                if self.selected_textbox != None:
                    self.textbox_update(event)

    def button_press(self, button):
        """
        Runs whenever a button is pressed
        """
        AudioPlayer.play_sound("click")

    def textbox_update(self, event):
        """
        Runs whenever a key is pressed and a textbox is selected
        """
        if event.key == pygame.K_BACKSPACE:
            self.selected_textbox['text'] = self.selected_textbox['text'][:-1]
        else:
            self.selected_textbox['text'] = self.selected_textbox['text'] + event.unicode
        font = pygame.font.SysFont(None, 25)
        self.selected_textbox['text_surf'] = get_text_surf(size=25, text=self.selected_textbox['text'], colour=(255, 255, 255), font=font)

    def change_error_message(self, text):
        """
        Changes the error message displayed
        """
        self.error_msg['surf'] = get_text_surf(size=25, text=text, colour=(255, 255, 255))

    def run(self):
        """
        Runs a frame of the main menu
        """
        while not self.kill_screen:
            self.dt = (time.time() - self.last_time)
            self.last_time = time.time()
            self.cursor_timer += self.dt
            if self.cursor_timer >= 1:
                self.cursor_timer = 0
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

        #self.images['bg'] = load_image("assets/images/main_menu.png")

        #Loads all the buttons in
        self.buttons = {}
        for i, data in enumerate((("Start Game", "game"), ("Options", "options_menu"), ("Leaderboard", "leaderboard"), ("Credits", "credits_menu"), ("Exit to Desktop", "exit"))):
            self.buttons[data[1]] = {
                'label': get_text_surf(size=40, text=data[0], colour=(255, 255, 255)), 
                'id': data[1],
                'rect': pygame.Rect(100, (i * 60) + 350, 300, 50)
            }
        
        self.buttons['sign_out'] = {
                'label': get_text_surf(size=20, text="Sign Out", colour=(255, 255, 255)), 
                'id': 'sign_out',
                'rect': pygame.Rect(1180, 670, 80, 30)
            }

        current_user = load_data()['logged_in']

        # Loads the text in
        self.text = [
            {'surf': get_text_surf(size=100, text="Treasure", colour=(255, 202, 24)), 'pos': None},
            {'surf': get_text_surf(size=100, text="Trove", colour=(255, 202, 24)), 'pos': None},
            {'surf': get_text_surf(size=20, text=f"Logged in as {current_user}", colour=(255, 255, 255)), 'pos': None}
        ]

        self.text[0]['pos'] = (250 - (self.text[0]['surf'].get_width() // 2), 100)
        self.text[1]['pos'] = (250 - (self.text[1]['surf'].get_width() // 2), 175)
        self.text[2]['pos'] = (1170 - self.text[2]['surf'].get_width(), self.buttons['sign_out']['rect'].centery - (self.text[2]['surf'].get_height() // 2))

    def button_press(self, button):
        super().button_press(button)
        if button['id'] == "sign_out":
            data = load_data()
            del data['logged_in']
            save_data(data)
            self.selected_screen = "selection"
        else:
            self.selected_screen = button['id']
        self.kill_screen = True


class OptionsMenu(Menu):
    def __init__(self, window, fps):
        super().__init__(window, fps)
        pygame.display.set_caption("Treasure Trove - Options")

        # Loads the buttons in
        self.buttons = {
            'decrease_res': {'label': get_text_surf(size=60, text="<", colour=(255, 255, 255)), 'id': 'decrease_res', 'rect': pygame.Rect((800, 250, 75, 75))},
            'increase_res': {'label': get_text_surf(size=60, text=">", colour=(255, 255, 255)), 'id': 'increase_res', 'rect': pygame.Rect((1100, 250, 75, 75))},
            'decrease_fps': {'label': get_text_surf(size=60, text="<", colour=(255, 255, 255)), 'id': 'decrease_fps', 'rect': pygame.Rect((800, 350, 75, 75))},
            'increase_fps': {'label': get_text_surf(size=60, text=">", colour=(255, 255, 255)), 'id': 'increase_fps', 'rect': pygame.Rect((1100, 350, 75, 75))},
            'main_menu': {'label': get_text_surf(size=40, text="Return to Main Menu", colour=(255, 255, 255)), 'id': 'main_menu', 'rect': pygame.Rect((self.display.get_width() // 2) - 200, self.display.get_height() - 125, 400, 50)}
        }

        # Loads the text
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
        if "fps" in button['id']:
            self.fps += 1 if button['id'] == "increase_fps" else -1
            data = load_data()
            data['options']['fps'] = self.fps
            save_data(data)
            self.text[4]['surf'] = get_text_surf(size=40, text=str(self.fps), colour=(255, 255, 255))

        elif "res" in button['id']:
            new_res = RESOLUTIONS[(RESOLUTIONS.index(self.window.get_size()) + (1 if button['id'] == "decrease_res" else -1)) % len(RESOLUTIONS)]
            pygame.display.quit()
            self.window = create_window(new_res)
            pygame.display.set_caption("Treasure Trove - Options Menu")
            data = load_data()
            data['options']['res'] = new_res
            save_data(data)
            self.text[3]['surf'] = get_text_surf(size=40, text=f"{new_res[0]}x{new_res[1]}", colour=(255, 255, 255))

        elif button['id'] == "main_menu":
            self.selected_screen = "main_menu"
            self.kill_screen = True


class CreditsMenu(Menu):
    def __init__(self, window, fps):
        super().__init__(window, fps)
        pygame.display.set_caption("Treasure Trove - Credits")

        # Loads the buttons
        self.buttons = {'main_menu': {'label': get_text_surf(size=40, text="Return to Main Menu", colour=(255, 255, 255)), 'id': 'main_menu', 'rect': pygame.Rect((self.display.get_width() // 2) - 200, self.display.get_height() - 125, 400, 50)}}

        # Loads all the text
        self.text = [{'surf': get_text_surf(size=70, text="Credits", colour=(255, 202, 24)), 'pos': None}]
        self.text[0]['pos'] = ((self.display.get_width() // 2) - (self.text[0]['surf'].get_width() // 2), 50)

        credits = [
            "|Created by: Muhammad-Ali Mohsin", 
            "",
            "|Programming, Artwork and Design",
            "  Muhammad-Ali Mohsin",
            "",
            "|Free assets used",
            "Player/Enemy Animations and Keyboard keys",
            "https://game-endeavor.itch.io/mystic-woods",
            "https://opengameart.org/content/free-keyboard-and-controllers-prompts-pack",
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
            "https://opengameart.org/content/game-over-bad-chest-sfx",
            "https://opengameart.org/content/single-key-press-sounds"
        ]

        # Creates text objects for all the credits
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
        if button['id'] == "main_menu":
            self.selected_screen = "main_menu"
            self.kill_screen = True


class LeaderboardMenu(Menu):
    def __init__(self, window, fps):
        super().__init__(window, fps)
        pygame.display.set_caption("Treasure Trove - Leaderboard")

        # Loads the buttons
        self.buttons = {'main_menu': {'label': get_text_surf(size=40, text="Return to Main Menu", colour=(255, 255, 255)), 'id': 'main_menu', 'rect': pygame.Rect((self.display.get_width() // 2) - 200, self.display.get_height() - 125, 400, 50)}}

        # Loads the text
        self.text = [{'surf': get_text_surf(size=70, text="Leaderboard", colour=(255, 202, 24)), 'pos': None}]
        self.text[0]['pos'] = ((self.display.get_width() // 2) - (self.text[0]['surf'].get_width() // 2), 50)

        # Loads all the high scores in and creates text objects for them
        high_scores = load_data()['scores']
        for i, score in enumerate(high_scores):
            surf = get_text_surf(size=35, text=f"{i + 1}) {score[0]} - {format_num(score[1])} Gold", colour=(255, 255, 255))
            self.text.append({
                'surf': surf, 
                'pos': ((self.display.get_width() // 2) - (surf.get_width() // 2), 200 + (i * 30))
            })

    def button_press(self, button):
        super().button_press(button)
        if button['id'] == "main_menu":
            self.selected_screen = "main_menu"
            self.kill_screen = True


class SignUpMenu(Menu):
    def __init__(self, window, fps):
        super().__init__(window, fps)
        pygame.display.set_caption("Treasure Trove - Sign Up")

        self.accounts = load_data()['accounts']

        # Changes the position of the error message
        self.error_msg = {'surf': None, 'pos': (self.display.get_width() // 2, self.display.get_height() - 260)}

        # Loads all the buttons in
        self.buttons = {
            'selection': {'label': get_text_surf(size=40, text="Return to Selection", colour=(255, 255, 255)), 'id': 'selection', 'rect': pygame.Rect(((self.display.get_width() // 2) - 200, self.display.get_height() - 125, 400, 50))},
            'sign_up': {'label': get_text_surf(size=40, text="Sign Up", colour=(255, 255, 255)), 'id': 'sign_up', 'rect': pygame.Rect(((self.display.get_width() // 2) - 100, self.display.get_height() - 225, 200, 50))}
        }

        # Loads the text in
        self.text = [
            {'surf': get_text_surf(size=70, text="Sign Up", colour=(255, 202, 24)), 'pos': None},
            {'surf': get_text_surf(size=40, text="Username", colour=(255, 202, 24)), 'pos': (300, 200)},
            {'surf': get_text_surf(size=40, text="Password", colour=(255, 202, 24)), 'pos': (300, 275)},
            {'surf': get_text_surf(size=40, text="Confirm Password", colour=(255, 202, 24)), 'pos': (300, 350)}
        ]
        self.text[0]['pos'] = ((self.display.get_width() // 2) - (self.text[0]['surf'].get_width() // 2), 50)

        # Loads all the textboxes in
        self.textboxes = {
            'username': {'id': 'username', 'rect': pygame.Rect(700, 200, 400, 40), 'text': "", 'text_surf': get_text_surf(size=20, text="", colour=(255, 255, 255))},
            'password': {'id': 'password', 'rect': pygame.Rect(700, 275, 400, 40), 'text': "", 'text_surf': get_text_surf(size=20, text="", colour=(255, 255, 255))},
            'confirm_password': {'id': 'confirm_password', 'rect': pygame.Rect(700, 350, 400, 40), 'text': "", 'text_surf': get_text_surf(size=20, text="", colour=(255, 255, 255))},

        }

    def button_press(self, button):
        super().button_press(button)
        if button['id'] == "selection":
            self.selected_screen = "selection"
            self.kill_screen = True
        elif button['id'] == "sign_up":
            validated = False
            # Checks whether the fields are empty
            if self.textboxes['username']['text'] == "" or self.textboxes['password']['text'] == "" or self.textboxes['confirm_password']['text'] == "":
                self.change_error_message("All fields must be completed")
            # Makes sure the username is long enough
            elif len(self.textboxes['username']['text']) < 3:
                self.change_error_message("Username must be at least 3 characters")
            # Makes sure the password is long enough
            elif len(self.textboxes['password']['text']) < 5:
                self.change_error_message("Password must be at least 5 characters")
            # Makes sure the password fields are equal
            elif self.textboxes['password']['text'] != self.textboxes['confirm_password']['text']:
                self.change_error_message("Passwords do not match")
            # Checks whether the username has been taken
            elif self.textboxes['username']['text'] in self.accounts:
                self.change_error_message("This username has been taken")
            else:
                self.accounts[self.textboxes['username']['text']] = get_hash(self.textboxes['password']['text'])
                data = load_data()
                data['accounts'] = self.accounts
                data['logged_in'] = self.textboxes['username']['text']
                save_data(data)
                validated = True
                self.selected_screen = "main_menu"
                self.kill_screen = True
            # Plays an error sound if validation was failed
            if not validated:
                AudioPlayer.play_sound("error")

    def textbox_update(self, event):
        super().textbox_update(event)
        # Replaces all text in the password fields with an asterisk '*'
        if "password" in self.selected_textbox['id']:
            font = pygame.font.SysFont(None, 25)
            self.selected_textbox['text_surf'] = get_text_surf(size=25, text=len(self.selected_textbox['text']) * '*', colour=(255, 255, 255), font=font)


class LoginMenu(Menu):
    def __init__(self, window, fps):
        super().__init__(window, fps)
        pygame.display.set_caption("Treasure Trove - Login")

        self.accounts = load_data()['accounts']

        # Changes the position of the error message
        self.error_msg = {'surf': None, 'pos': (self.display.get_width() // 2, self.display.get_height() - 260)}

        # Loads all the buttons in
        self.buttons = {
            'selection': {'label': get_text_surf(size=40, text="Return to Selection", colour=(255, 255, 255)), 'id': 'selection', 'rect': pygame.Rect(((self.display.get_width() // 2) - 200, self.display.get_height() - 125, 400, 50))},
            'login': {'label': get_text_surf(size=40, text="Login", colour=(255, 255, 255)), 'id': 'login', 'rect': pygame.Rect(((self.display.get_width() // 2) - 100, self.display.get_height() - 225, 200, 50))}
        }

        # Loads the text in
        self.text = [
            {'surf': get_text_surf(size=70, text="Login", colour=(255, 202, 24)), 'pos': None},
            {'surf': get_text_surf(size=40, text="Username", colour=(255, 202, 24)), 'pos': (300, 275)},
            {'surf': get_text_surf(size=40, text="Password", colour=(255, 202, 24)), 'pos': (300, 350)}
        ]
        self.text[0]['pos'] = ((self.display.get_width() // 2) - (self.text[0]['surf'].get_width() // 2), 50)

        # Loads all the textboxes in
        self.textboxes = {
            'username': {'id': 'username', 'rect': pygame.Rect(700, 275, 400, 40), 'text': "", 'text_surf': get_text_surf(size=20, text="", colour=(255, 255, 255))},
            'password': {'id': 'password', 'rect': pygame.Rect(700, 350, 400, 40), 'text': "", 'text_surf': get_text_surf(size=20, text="", colour=(255, 255, 255))},
        }

    def button_press(self, button):
        super().button_press(button)
        if button['id'] == "selection":
            self.selected_screen = "selection"
            self.kill_screen = True
        elif button['id'] == "login":
            validated = False
            # Checks whether the fields are empty
            if self.textboxes['username']['text'] == "" or self.textboxes['password']['text'] == "":
                self.change_error_message("All fields must be completed")
            # Checks whether the username has been taken
            elif self.textboxes['username']['text'] not in self.accounts:
                self.change_error_message("Username not found")
            elif get_hash(self.textboxes['password']['text']) != self.accounts[self.textboxes['username']['text']]:
                self.change_error_message("Incorrect password")
            else: 
                data = load_data()
                data['logged_in'] = self.textboxes['username']['text']
                save_data(data)
                validated = True
                self.selected_screen = "main_menu"
                self.kill_screen = True
            # Plays an error sound if validation was failed
            if not validated:
                AudioPlayer.play_sound("error")

    def textbox_update(self, event):
        super().textbox_update(event)
        # Replaces all text in the password fields with an asterisk '*'
        if "password" in self.selected_textbox['id']:
            font = pygame.font.SysFont(None, 25)
            self.selected_textbox['text_surf'] = get_text_surf(size=25, text=len(self.selected_textbox['text']) * '*', colour=(255, 255, 255), font=font)


class SelectionMenu(Menu):
    def __init__(self, window, fps):
        super().__init__(window, fps)
        pygame.display.set_caption("Treasure Trove - Login/Signup")

        # Loads all the buttons in
        self.buttons = {
            'signup': {'label': get_text_surf(size=40, text="Sign Up", colour=(255, 255, 255)), 'id': 'signup', 'rect': pygame.Rect(((self.display.get_width() // 2) - 225, self.display.get_height() // 2 - 25, 200, 50))},
            'login': {'label': get_text_surf(size=40, text="Login", colour=(255, 255, 255)), 'id': 'login', 'rect': pygame.Rect(((self.display.get_width() // 2) + 25, self.display.get_height() // 2 - 25, 200, 50))},
            'exit': {'label': get_text_surf(size=40, text="Exit to Desktop", colour=(255, 255, 255)), 'id': 'exit', 'rect': pygame.Rect((self.display.get_width() // 2) - 150, 500, 300, 40)}
        }

    def button_press(self, button):
        super().button_press(button)
        self.selected_screen = button['id']
        self.kill_screen = True