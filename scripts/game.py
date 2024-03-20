import time
import random
import math

import pygame

from sympy import symbols, Eq, solve, simplify

from scripts.animations import AnimationHandler, load_animation, load_animation_library
from scripts.hud import HUD
from scripts.entities import Player, Enemy
from scripts.maze import generate_maze
from scripts.effects import ParticleHandler
from scripts.utils import AudioPlayer, load_image, load_images, load_data, save_data, get_text_surf, scale_coord_to_new_res, format_num, update_scores

TRANSITION_DURATION = 1
DAY_DURATION = 180

class Maths:
    def generate_algebra():
        x = symbols('x')
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        c = random.randint(1, 10)
        equation = Eq(a * x + b, c)
        solution = solve(equation, x)
        return "Solve for x", f"{a}x + {b} = {c}", solution[0]
    
    def generate_fraction():
        fraction = f"{random.randint(1, 100)} / {random.randint(1, 100)}"
        return "Simplify the following", fraction, simplify(fraction)
    
    def generate_arithmetic():
        expression = str(random.randint(1, 100))
        for i in range(random.randint(1, 3)):
            expression += f" {random.choice(['+', '-'])} {random.randint(1, 100)}"
        return "Simplify the following", expression, eval(expression)

class Treasure:
    def __init__(self, game):
        self.game = game
        self.loc = None
        self.animation = AnimationHandler.create_animation()
        self.animation.change_animation_library(self.game.animations['treasure'])
        self.released_gold = False
        self.popup = False
        self.glow_timer = 0
        self.reset()
    
    def get_rect(self):
        return pygame.Rect((self.loc[0] * self.game.maze.tile_size) + 8, (self.loc[1] * self.game.maze.tile_size) + 8, 16, 16)

    def reset(self):
        top_left_loc = self.game.maze.get_loc(self.game.camera_displacement)
        bottom_right_loc = self.game.maze.get_loc((self.game.camera_displacement[0] + self.game.display.get_width(), self.game.camera_displacement[1] + self.game.display.get_height()))
        top_left_loc = (max(0, top_left_loc[0]), max(0, top_left_loc[1]))
        bottom_right_loc = (min(self.game.maze.resolution[0], bottom_right_loc[0]), min(self.game.maze.resolution[1], bottom_right_loc[1]))
        loc = self.game.maze.get_random_loc("path", (top_left_loc, bottom_right_loc), 'outside')
        self.loc = loc
        self.animation.change_animation("closed")

    def open(self):
        if len(self.game.tutorial) != 0 and "treasure" not in self.game.tutorial[0]['name']:
            return
        self.game.shake_screen(10, 0.3)
        self.animation.change_animation("open")
        AudioPlayer.play_sound("chest")

    def update(self):
        if self.animation.current_animation == "open" and self.animation.frame == len(self.animation.animation_library[self.animation.current_animation]['images']) - 2 and not self.popup:
            self.game.question_flags['popup'] = True
            self.game.generate_maths_question()
            self.popup = True

        if self.animation.current_animation == "open" and self.animation.frame == len(self.animation.animation_library[self.animation.current_animation]['images']) - 1 and not self.released_gold:
            for i in range(10):
                ParticleHandler.create_particle("gold", self.game, ((self.loc[0] * self.game.maze.tile_size) + 8 + random.randint(-5, 5), (self.loc[1] * self.game.maze.tile_size) + 8 + random.randint(-5, 5)), velocity=(random.uniform(2, -2), random.uniform(-4, -2)))
            self.released_gold = True

        if self.animation.current_animation == "open" and self.animation.done:
            # Creates dust particles which fly off the treasure to show it's disappearing
            for angle in (math.pi * 1/4, math.pi * 2/4, math.pi * 3/4, math.pi, math.pi * 5/4, math.pi * 6/4, math.pi * 7/4, math.pi * 8/4):
                ParticleHandler.create_particle("dust", self.game, ((self.loc[0] * self.game.maze.tile_size) + 8, (self.loc[1] * self.game.maze.tile_size) + 8), speed=random.uniform(1, 2), angle=angle)
 
            self.reset()
            self.released_gold = False
            self.popup = False
            self.game.wave += 1
            self.game.spawn_enemies()

        self.glow_timer = (self.glow_timer + self.game.dt * 2) % (2 * math.pi)

    def draw(self):
        img = self.animation.get_img()
        pos = [(self.loc[i] * self.game.maze.tile_size) - self.game.camera_displacement[i] for i in range(2)]
        self.game.display.blit(img, pos)
        center = [(self.loc[i] * self.game.maze.tile_size) + self.game.maze.tile_size // 2 for i in range(2)]
        self.game.glow(center, (255, 255, 100), 30 + round(5 * math.sin(self.glow_timer) + random.random()))
        self.game.glow(center, (255, 255, 255), 15 + round(3 * math.sin(self.glow_timer) + random.random()))

class Game:
    def __init__(self, window, fps):
        pygame.display.set_caption("Treasure Trove - Playing game")
        self.kill_screen = False
        self.fps = fps
        self.window = window
        self.display = pygame.Surface((426, 240))
        self.larger_display = pygame.Surface((1280, 720)).convert_alpha()
        self.clock = pygame.time.Clock()

        # Variables about the transition
        self.transition_surf = pygame.Surface(self.larger_display.get_size())
        self.transition_surf.set_colorkey((255, 255, 255))
        self.transition_timer = 0
        self.end_transition = False

        # Variables about the camera
        self.camera_displacement = [0, 0]
        self.screen_shake = [0, 0]

        # Lighting
        self.light_images = {}
        self.light_map = pygame.Surface(self.display.get_size()).convert_alpha()

        # Loads all the images in
        self.images = {
            'hedge': load_images("assets/images/hedges"),
            'path': load_images("assets/images/paths"),
            'flowers': load_images("assets/images/flowers"),
            'healthbar': load_image("assets/images/healthbar.png"),
            'gold_pouch': load_image("assets/images/gold_pouch.png"),
            'compass_base': load_image("assets/images/compass_base.png"),
            'compass_spinner': load_image("assets/images/compass_spinner.png"),
            'box': load_image("assets/images/box.png"),
            'box_2': load_image("assets/images/box_2.png"),
            'grey_screen': pygame.Surface(self.display.get_size()).convert_alpha(),
            'arrow_keys': load_image("assets/images/keys/arrow_keys.png"),
            'z_key': load_image("assets/images/keys/z_key.png"),
            'x_key': load_image("assets/images/keys/x_key.png"),
            'c_key': load_image("assets/images/keys/c_key.png"),
            'spacebar': load_image("assets/images/keys/spacebar.png"),
            'textbox': load_image("assets/images/textbox.png"),
            'light': load_image("assets/images/light.png"),
            'dash_icon': load_image("assets/images/dash_icon.png"),
            'explode_icon': load_image("assets/images/explode_icon.png"),
            'spiral_icon': load_image("assets/images/spiral_icon.png"),
        }

        # Loads all the animations in
        self.animations = {
            'player': load_animation_library("assets/animations/player"),
            'blue_slime': load_animation_library("assets/animations/slime"),
            'treasure': load_animation_library("assets/animations/treasure"),
            'dirt': {'default': load_animation("assets/particles/dirt", (0.1, 0.1, 0.1), False)},
            'leaves': {'default': load_animation("assets/particles/leaves", (0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2), False)},
            'experience': {'default': load_animation("assets/particles/experience", (0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1), True)},
            'blue_slime_particle': {'default': load_animation("assets/particles/slime", (0.1, 0.1, 0.1, 0.1), False)},
            'dust': {'default': load_animation("assets/particles/dust", (0.1, 0.1, 0.1, 0.1), False)},
            'gold': {'default': load_animation("assets/particles/gold", (10, 10), True)},
            'bee': {'default': load_animation("assets/particles/bee", (0.1, 0.1, 0.1), True)},
            'player_dashing': {'default': load_animation("assets/particles/player_dashing", (0.05, 0.05, 0.05, 0.05), False)},
            'plus_one': {'default': load_animation("assets/particles/plus_one", (0.1, 0.1), False)}
        }

        # Creates new_animations for the slime variants
        colors = {
            'red': ((80, 0, 0), (135, 0, 0), (185, 0, 0), (200, 45, 45), (200, 45, 45), (200, 45, 45)),
            'purple': ((25, 9, 53), (96, 36, 128), (122, 47, 149), (154, 71, 151), (85, 21, 108), (128, 16, 40))
            }
        for color in colors:
            self.animations[color + "_slime"] = load_animation_library("assets/animations/slime")
            self.animations[color + '_slime_particle'] = {'default': load_animation("assets/particles/slime", (0.1, 0.1, 0.1, 0.1), False)}
            for animation in self.animations[color + "_slime"]:
                for img in self.animations[color + "_slime"][animation]['images'] + self.animations[color + '_slime_particle']['default']['images']:
                    pygame.transform.threshold(dest_surface=img, surface=img, search_color=(29, 35, 93), set_color=colors[color][0], inverse_set=True) # Border color
                    pygame.transform.threshold(dest_surface=img, surface=img, search_color=(66, 91, 158), set_color=colors[color][1], inverse_set=True) # First layer
                    pygame.transform.threshold(dest_surface=img, surface=img, search_color=(77, 138, 179), set_color=colors[color][2], inverse_set=True) # Second layer
                    pygame.transform.threshold(dest_surface=img, surface=img, search_color=(101, 177, 184), set_color=colors[color][3], inverse_set=True) # Primary color
                    pygame.transform.threshold(dest_surface=img, surface=img, search_color=(51, 65, 138), set_color=colors[color][4], inverse_set=True) # Mouth
                    pygame.transform.threshold(dest_surface=img, surface=img, search_color=(158, 46, 70), set_color=colors[color][5], inverse_set=True) # Tongue

        # Image rescaling
        self.images['compass_spinner'] = pygame.transform.scale(self.images['compass_spinner'], (self.images['compass_spinner'].get_width() * 3, self.images['compass_spinner'].get_height() * 3))
        self.images['compass_base'] = pygame.transform.scale(self.images['compass_base'], (self.images['compass_base'].get_width() * 3, self.images['compass_base'].get_height() * 3))
        self.images['gold_pouch'] = pygame.transform.scale(self.images['gold_pouch'], (self.images['gold_pouch'].get_width() * 3, self.images['gold_pouch'].get_height() * 3))
        self.images['healthbar'] = pygame.transform.scale(self.images['healthbar'], (self.images['healthbar'].get_width() * 3, self.images['healthbar'].get_height() * 3))
        self.images['box'] = pygame.transform.scale(self.images['box'], (self.images['box'].get_width() * 3, self.images['box'].get_height() * 3))
        self.images['box_2'] = pygame.transform.scale(self.images['box_2'], (self.images['box_2'].get_width() * 3, self.images['box_2'].get_height() * 3))

        # Changes transparency
        for img in self.animations['dirt']['default']['images']:
            img.set_alpha(150)
        self.images['grey_screen'].set_alpha(175)

        # Loads in numbers
        self.number_images = []
        for i in range(6):
            self.number_images.append(get_text_surf(size=45, text=str(i), colour=(70, 50, 10)))

        # Variables about the game
        self.maze = generate_maze(self, tile_size=32, maze_resolution=(25, 25), removed_tiles=25)
        self.player = Player(self, self.maze.get_random_loc("path"), (14, 20), 2, 100)
        self.enemies = []
        self.spikes = []
        self.gold = 0
        self.wave = 0
        self.killed = 0
        self.paused = False
        self.game_over = False
        self.treasure = Treasure(self)
        self.special_attacks = [3, 3, 3]
        self.maths_question = {'text': "", 'text_surf': get_text_surf(size=20, text="", colour=(255, 255, 255)), 'cursor_timer': 0}
        self.question_flags = {'popup': False, 'correct': [False, False, False], 'last_question': -1, 'correct_timer': 0, 'close_timer': 0, 'close_popup': False}

        # Variables about the tutorial
        self.tutorial_text_timer = 0
        tutorial = [
            {'name': "movement", 'img': "arrow_keys", 'text': "Use the arrow keys to move around", 'directions': set()},
            {'name': "treasure", 'text': "Follow the red hand of the compass to find the treasure", 'font_size': 23},
            {'name': "attack_treasure", 'img': "spacebar", 'text': "Press SPACE to attack the treasure chest and open it", 'font_size': 23},
            {'name': "maths_question_0", 'text': "Solve the maths question to gain a special ability", 'timer': 3, 'font_size': 25},
            {'name': "maths_question_1", 'text': "Each question will give a different ability"},
            {'name': "slimes_0", 'text': "Slimes will spawn in waves", 'timer': 2},
            {'name': "slimes_1", 'text': "Slimes can be defeated using special abilities", 'timer': 2},
            {'name': "slimes_2", 'text': "You can see how many abilities you have in the bottom left", 'timer': 2, 'font_size': 22},
            {'name': "slimes_3", 'text': "Match the colours of the ability and the slime to defeat them", 'timer': 2, 'font_size': 22},
            {'name': "dash_attack", 'img': "z_key", 'text': "Find a purple enemy and use Z to dash into them", 'font_size': 27},
            {'name': "spiral_attack", 'img': "x_key", 'text': "Find a blue enemy and use X to spiral attack", 'font_size': 27},
            {'name': "explosion_attack", 'img': "c_key", 'text': "Find a red enemy and use C to explode attack", 'font_size': 27},
            {'name': "end_0", 'text': "You have a limited number of special attacks", 'timer': 2},
            {'name': "end_1", 'text': "Replenish attacks by solving maths questions", 'timer': 2},
            {'name': "end_2", 'text': "Every time you open a chest, you will collect gold", 'timer': 2, 'font_size': 27},
            {'name': "end_3", 'text': "Let's see how much gold you can collect!", 'timer': 2},
            {'name': "end_4 (treasure)", 'text': "(Hint: Open a chest to spawn the next wave)", 'timer': 5, 'font_size': 20}
        ]
        data = load_data()
        self.tutorial = [] if 'completed_tutorial' in data['accounts'][data['logged_in']] else tutorial

        # Graphical variables
        self.hud = HUD(self)
        self.wind_intensity = random.uniform(-1, 1)

        # Loads the background music and ambience and plays it on a loop
        music = pygame.mixer.Sound("assets/sfx/music.wav")
        music.set_volume(0.7)
        music.play(-1, fade_ms=1000)
        ambience = pygame.mixer.Sound("assets/sfx/ambience.wav")
        ambience.play(-1, fade_ms=1000)

        # Loads all sfx sounds
        AudioPlayer.load_sounds("running", "assets/sfx/running", 0.2, True)
        AudioPlayer.load_sound("player_attack", "assets/sfx/player_attack.wav", 0.8)
        AudioPlayer.load_sound("dash_attack", "assets/sfx/dash_attack.wav", 0.5)
        AudioPlayer.load_sound("spiral_attack", "assets/sfx/spiral_attack.wav", 0.5)
        AudioPlayer.load_sound("explosion_attack", "assets/sfx/explosion_attack.wav", 0.5)
        AudioPlayer.load_sound("player_death", "assets/sfx/player_death.wav", 1)
        AudioPlayer.load_sound("hit", "assets/sfx/hit.wav", 1)

        AudioPlayer.load_sounds("enemy_attack", "assets/sfx/enemy_attack", 0.8, True)
        AudioPlayer.load_sound("enemy_death", "assets/sfx/enemy_death.wav", 1)

        AudioPlayer.load_sound("health", "assets/sfx/health.wav", 0.7)
        AudioPlayer.load_sound("gold", "assets/sfx/gold.wav", 0.7)
        AudioPlayer.load_sound("experience", "assets/sfx/experience.wav", 0.3)
        AudioPlayer.load_sound("treasure", "assets/sfx/treasure.wav", 0.1)
        AudioPlayer.load_sound("plus_one", "assets/sfx/plus_one.wav", 1)
        AudioPlayer.load_sound("plus_one_spawn", "assets/sfx/plus_one_spawn.wav", 1)

        AudioPlayer.load_sound("chest", "assets/sfx/chest.wav", 0.1)
        AudioPlayer.load_sound("game_over", "assets/sfx/game_over.wav", 1)
        AudioPlayer.load_sounds("key_press", "assets/sfx/keys", 0.1, True, True)
        AudioPlayer.load_sound("correct", "assets/sfx/correct.wav", 1)
        AudioPlayer.load_sound("wrong", "assets/sfx/wrong.wav", 1)

        # Time
        self.dt = 0
        self.last_time = time.time()
        self.time = 115 # Midday

    def glow(self, pos, color, radius):
        radius = round(radius)
        if (color, radius) not in self.light_images:
            img = pygame.transform.scale(self.images['light'].copy(), (radius * 2, radius * 2))
            img.set_colorkey((0, 0, 0))
            img2 = img.copy()
            img.fill(color)
            img.blit(img2, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.light_images[(color, radius)] = img
        
        self.light_map.blit(self.light_images[(color, radius)], (pos[0] - self.light_images[(color, radius)].get_width() // 2 - self.camera_displacement[0], pos[1] - self.light_images[(color, radius)].get_height() // 2 - self.camera_displacement[1]), special_flags=pygame.BLEND_RGB_ADD)

    def handle_events(self):
        """
        Handles all pygame events such as button presses
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.kill_screen = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player.moving['left'] = True
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.moving['right'] = True
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.player.moving['up'] = True
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.player.moving['down'] = True
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                if event.key == pygame.K_BACKSPACE:
                    if self.paused or self.game_over: 
                        self.transition_timer = -TRANSITION_DURATION
                        self.end_transition = True
                if event.key == pygame.K_SPACE:
                    if self.player.animation.current_animation != "death": self.player.attack()
                if event.key == pygame.K_z:
                    if self.player.animation.current_animation != "death": self.player.dash()
                if event.key == pygame.K_c:
                    if self.player.animation.current_animation != "death": self.player.explode()
                if event.key == pygame.K_x:
                    if self.player.animation.current_animation != "death": self.player.spiral()
                if self.question_flags['popup']:
                    self.maths_textbox_update(event)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player.moving['left'] = False
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.moving['right'] = False
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.player.moving['up'] = False
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.player.moving['down'] = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.player.animation.current_animation != "death": self.player.attack()

    def create_enemy(self, color=None):
        """
        Spawns an enemy in a random location
        """
        top_left_loc = self.maze.get_loc(self.camera_displacement)
        bottom_right_loc = self.maze.get_loc((self.camera_displacement[0] + self.display.get_width(), self.camera_displacement[1] + self.display.get_height()))
        top_left_loc = (max(0, top_left_loc[0]), max(0, top_left_loc[1]))
        bottom_right_loc = (min(self.maze.resolution[0], bottom_right_loc[0]), min(self.maze.resolution[1], bottom_right_loc[1]))
        loc = self.maze.get_random_loc("path", (top_left_loc, bottom_right_loc), 'outside')

        colors = {'red': 0, 'blue': 0, 'purple': 0}
        for enemy in self.enemies:
            colors[enemy.color] += 1

        color = sorted(list(colors), key=lambda color: colors[color])[0] if color == None else color

        self.enemies.append(Enemy(self, loc, (16, 16), random.uniform(1, 2), 30, color))

    def spawn_enemies(self):
        """
        Spawns a bunch of enemies based on the current wave
        """
        num = 0 if len(self.tutorial) != 0 else max(1, round(math.log(self.wave, 1.3)))
        for i in range(num):
            self.create_enemy()

    def shake_screen(self, magnitude, duration):
        """
        Shakes the screen
        """
        self.screen_shake = [magnitude, duration]

    def update_tutorial(self):
        """
        Updates the tutorial by updating the text and the stage of the tutorial
        """
        tutorial = self.tutorial[0]
        self.special_attacks = [3, 3, 3]

        # Adds the completed text as an empty string to the dictionary 
        if 'completed_text' not in tutorial:
            tutorial['completed_text'] = ""

        # Updates the timer of the tutorial
        if 'timer' in tutorial and tutorial['completed_text'] == True:
            tutorial['timer'] -= self.dt
            if tutorial['timer'] <= 0:
                self.tutorial.remove(tutorial)

        # Updates the text surface to show the typing animation
        if tutorial['completed_text'] != True:
            self.tutorial_text_timer += self.dt
            if self.tutorial_text_timer > 0.05:
                tutorial['completed_text'] = tutorial['text'][:len(tutorial['completed_text']) + 1]
                tutorial['text_surf'] = get_text_surf(tutorial['font_size'] if 'font_size' in tutorial else 30, tutorial['completed_text'], (110, 74, 17))
                self.tutorial_text_timer = 0
                AudioPlayer.play_sound("key_press")
                if tutorial['completed_text'] == tutorial['text']:
                    tutorial['completed_text'] = True

        # Checks what the tutorial is and updates it appropriately
        if tutorial['name'] == "movement":
            if self.player.moving['left']: tutorial['directions'].add('left')
            if self.player.moving['right']: tutorial['directions'].add('right')
            if self.player.moving['up']: tutorial['directions'].add('up')
            if self.player.moving['down']: tutorial['directions'].add('down')
            if len(tutorial['directions']) == 4:
                self.tutorial.remove(tutorial)

        elif tutorial['name'] == "attack_treasure":
            if self.question_flags['popup']:
                self.tutorial.remove(tutorial)
                
        elif tutorial['name'] == "maths_question_1":
            if not self.question_flags['popup']:
                self.tutorial.remove(tutorial)

        elif tutorial['name'] == "treasure":
            if self.maze.tiles[self.maze.get_loc(self.player.get_center())] in self.maze.get_neighbours(self.maze.tiles[self.treasure.loc], diagonals=True):
                self.tutorial.remove(tutorial)

        elif tutorial['name'] in ["dash_attack", "spiral_attack", "explosion_attack"]:
            if 'has_spawned' not in tutorial:
                self.create_enemy({'dash_attack': 'purple', 'spiral_attack': 'blue', 'explosion_attack': 'red'}[tutorial['name']])
                tutorial['has_spawned'] = True
            if len(self.enemies) == 0:
                self.tutorial.remove(tutorial)

        # Marks the tutorial as completed
        if len(self.tutorial) == 0:
            data = load_data()
            data['accounts'][data['logged_in']]['completed_tutorial'] = True
            save_data(data)

    def get_daylight(self):
        """
        Returns a color scale for the time of day
        """
        # Defines the color scales for different times
        morning_color = pygame.Vector3(1.0, 0.9, 0.8);
        midday_color = pygame.Vector3(1.0, 1.0, 1.0);
        evening_color = pygame.Vector3(0.55, 0.4, 0.3);
        night_color = pygame.Vector3(0.2, 0.15, 0.15);

        daytime = self.time / DAY_DURATION
        ranges = ((0, 0.2), (0.2, 0.25), (0.25, 0.5), (0.5, 0.7), (0.7, 0.8), (0.8, 0.85), (0.85, 1))
        colors = ((night_color, night_color), (night_color, morning_color), (morning_color, midday_color), (midday_color, midday_color), (midday_color, evening_color), (evening_color, night_color), (night_color, night_color))

        for i, range in enumerate(ranges):
            if daytime >= range[0] and daytime <= range[1]:
                daylight = ((daytime - range[0]) / (range[1] - range[0]) * (colors[i][1] - colors[i][0])) + colors[i][0]
                break

        return daylight
    
    def generate_maths_question(self):
        types = [Maths.generate_algebra, Maths.generate_arithmetic, Maths.generate_fraction]
        self.question_flags['last_question'] = (self.question_flags['last_question'] + 1) % 3
        question = types[self.question_flags['last_question']]()
        font = pygame.font.SysFont(None, 30)
        self.maths_question = {
            'text': "", 
            'text_surf': get_text_surf(size=20, text="", colour=(255, 255, 255)), 
            'cursor_timer': 0,
            'instruction_surf': get_text_surf(size=45, text=question[0], colour=(172, 116, 27)),
            'question_surf': get_text_surf(size=35, text=question[1], colour=(172, 116, 27), font=font),
            'answer': str(question[2])
            }
        
    def draw_maths_popup(self):
        """
        Draws a screen with a given text as the center (Used for the pause screen and game over screen)
        """
        # Closes the popup if all questions have been answered
        self.question_flags['correct_timer'] = max(0, self.question_flags['correct_timer'] - self.dt)
        self.question_flags['close_timer'] = max(0, self.question_flags['close_timer'] - self.dt)
        if self.question_flags['close_timer'] == 0 and self.question_flags['close_popup'] and self.question_flags['correct_timer'] == 0:
            self.question_flags['popup'] = False
            self.question_flags['close_popup'] = False
            for i in range(len(self.question_flags['correct'])):
                if self.question_flags['correct'][i]:
                    ParticleHandler.create_particle("plus_one", self, self.player.pos, velocity=(-2 + (i / 2), random.uniform(-4, -2)), attack_type=i)
            self.question_flags['correct'] = [False, False, False]

        # Draws the grey screen, and the red and green background 
        self.display.blit(self.images['grey_screen'], (0, 0))
        correct = self.question_flags['correct'].count(True) - (self.question_flags['correct_timer'] / 0.5)
        pygame.draw.rect(self.larger_display, (187, 37, 42), ((self.larger_display.get_width() // 2) - 258, (self.larger_display.get_height() // 2) - 138, 516, 276))
        pygame.draw.rect(self.larger_display, (87, 165, 42), ((self.larger_display.get_width() // 2) - 258, (self.larger_display.get_height() // 2) - 138 + (276 * (1 - (correct / 3))), 516, 276 * correct / 3))

        # Draws the box and the question
        box_pos = ((self.larger_display.get_width() // 2) - (self.images['box_2'].get_width() // 2), (self.larger_display.get_height() // 2) - (self.images['box_2'].get_height() // 2))
        self.larger_display.blit(self.images['box_2'], box_pos)
        self.larger_display.blit(self.maths_question['instruction_surf'], ((self.larger_display.get_width() // 2) - (self.maths_question['instruction_surf'].get_width() // 2), (self.larger_display.get_height() // 2) - (self.maths_question['instruction_surf'].get_height() // 2) - 60))
        self.larger_display.blit(self.maths_question['question_surf'], ((self.larger_display.get_width() // 2) - (self.maths_question['question_surf'].get_width() // 2), (self.larger_display.get_height() // 2) - (self.maths_question['question_surf'].get_height() // 2) - 20))
        
        # Draws the textbox
        rect = pygame.Rect((self.larger_display.get_width() // 2) - 150, (self.larger_display.get_height() // 2) + 50, 300, 40)
        outline_rect = pygame.Rect((self.larger_display.get_width() // 2) - 155, (self.larger_display.get_height() // 2) + 45, 310, 50)
        pygame.draw.rect(self.larger_display, (110, 74, 17), outline_rect)
        pygame.draw.rect(self.larger_display, (172, 116, 27), rect)
        self.larger_display.blit(self.maths_question['text_surf'], (rect.centerx - (self.maths_question['text_surf'].get_width() // 2), rect.centery - (self.maths_question['text_surf'].get_height() // 2)))

        # Draws the cursor on the textbox
        self.maths_question['cursor_timer'] += self.dt
        if self.maths_question['cursor_timer'] >= 1:
            self.maths_question['cursor_timer'] = 0
        if self.maths_question['cursor_timer'] <= 0.5:
            pygame.draw.rect(self.larger_display, (110, 74, 17), (rect.centerx + (self.maths_question['text_surf'].get_width() // 2) + 5, rect.centery - 13, 3, 26))

    def maths_textbox_update(self, event):
        """
        Runs when the maths textbox is updated
        """
        if event.key == pygame.K_BACKSPACE:
            self.maths_question['text'] = self.maths_question['text'][:-1]

        elif event.key == pygame.K_RETURN:
            if self.maths_question['text'] == self.maths_question['answer']:
                self.question_flags['correct'][self.question_flags['last_question']] = True
                self.question_flags['correct_timer'] = 0.5
                AudioPlayer.play_sound("correct")
            else:
                AudioPlayer.play_sound("wrong")
            
            if self.question_flags['last_question'] != 2:
                self.generate_maths_question()
            else:
                self.question_flags['close_popup'] = True
                self.question_flags['close_timer'] = 1

        elif event.unicode.lower() in "0123456789/-":
            if len(self.maths_question['text']) <= 10:
                self.maths_question['text'] = self.maths_question['text'] + event.unicode

        font = pygame.font.SysFont(None, 30)
        self.maths_question['text_surf'] = get_text_surf(size=30, text=self.maths_question['text'], colour=(240, 230, 190), font=font)

    def update_display(self):
        """
        Calls all functions to update the display
        """
        # Clears the display
        self.display.fill((35, 72, 39))
        self.larger_display.fill((0, 0, 0, 0))
        self.light_map.fill((0, 0, 0))

        # Draws all maze elements
        self.maze.draw()
        self.treasure.draw()

        # Updates and draws the particles
        ParticleHandler.update()

        # Draws all entities
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()

        # Draws all spikes
        for spike in self.spikes:
            spike.draw()

        # Draws the HUD
        self.hud.update()

        # Draws the maths popup
        if self.question_flags['popup'] and not (self.paused or self.game_over):
            self.draw_maths_popup()

        # Draws the tutorial
        if len(self.tutorial) != 0 and not (self.paused or self.game_over):
            pos = scale_coord_to_new_res((self.player.pos[0] + self.player.size[0] // 2 - self.camera_displacement[0], self.player.pos[1] - self.camera_displacement[1] - 5), self.display.get_size(), self.larger_display.get_size())
            self.larger_display.blit(self.images['textbox'], (self.larger_display.get_width() // 2 - self.images['textbox'].get_width() // 2 + 100, self.larger_display.get_height() - 100))
            if 'text_surf' in self.tutorial[0]:
                self.larger_display.blit(self.tutorial[0]['text_surf'], (self.larger_display.get_width() // 2 - self.tutorial[0]['text_surf'].get_width() // 2 + 100, self.larger_display.get_height() - 80))
            if 'img' in self.tutorial[0]:
                self.larger_display.blit(self.images[self.tutorial[0]['img']], (pos[0] - self.images[self.tutorial[0]['img']].get_width() // 2, pos[1] - self.images[self.tutorial[0]['img']].get_height()))

        # Draws the transition
        if self.transition_timer != TRANSITION_DURATION:
            self.transition_surf.fill((0, 0, 0))
            pygame.draw.circle(self.transition_surf, (255, 255, 255), (self.transition_surf.get_width() // 2, self.transition_surf.get_height() // 2), ((self.transition_surf.get_width() * 3/4) * (abs(self.transition_timer) / TRANSITION_DURATION)))

            # Blits the transition surface onto the larger display
            self.larger_display.blit(self.transition_surf, (0, 0))

        if self.screen_shake[1] > 0 and not (self.paused or self.game_over or self.question_flags['popup']):
            screen_shake = (random.random() * self.screen_shake[0], random.random() * self.screen_shake[0])
            self.display.blit(self.display, screen_shake)

        self.window.update(uniforms={
            'screen_texture': self.display, 'ldisplay_texture': self.larger_display, 'light_map': self.light_map, 
            'time': self.time, 'daylight': self.get_daylight(), 'screen': 0
            })

    def run(self):
        """
        Runs the game loop
        """
        while not self.kill_screen:
            # Calculates the change in time
            self.dt = (time.time() - self.last_time)
            self.last_time = time.time()
            self.time = (self.time + self.dt) % 180
            self.multi = self.dt * 60
            if len(self.tutorial) != 0:
                self.update_tutorial()
            if not self.paused and not self.game_over and not self.question_flags['popup']:

                # Plays the running sound if the player is running
                if (self.player.moving['right'] or self.player.moving['left'] or self.player.moving['up'] or self.player.moving['down']) and self.player.special_attack['name'] == None:
                    AudioPlayer.play_sound("running")

                # Counts down the screen shake
                self.screen_shake[1] = max(self.screen_shake[1] - self.dt, 0)

                # Randomly changes the wind intensity
                if random.random() < 0.005:
                    self.wind_intensity = random.uniform(-1, 1)

                # Spawns leaves from the hedges that are on the screen
                if random.random() < 0.1:
                    top_left_loc = self.maze.get_loc(self.camera_displacement)
                    bottom_right_loc = self.maze.get_loc((self.camera_displacement[0] + self.display.get_width(), self.camera_displacement[1] + self.display.get_height()))
                    top_left_loc = (max(0, top_left_loc[0]), max(0, top_left_loc[1]))
                    bottom_right_loc = (min(self.maze.resolution[0], bottom_right_loc[0]), min(self.maze.resolution[1], bottom_right_loc[1]))
                    loc = self.maze.get_random_loc("hedge", (top_left_loc, bottom_right_loc))
                    if random.random() < 0.1:
                        ParticleHandler.create_particle("bee", self, ((loc[0] * self.maze.tile_size) + (self.maze.tile_size // 2),  (loc[1] * self.maze.tile_size) + (self.maze.tile_size // 4)), speed=random.uniform(0.1, 0.5))
                    ParticleHandler.create_particle("leaf", self, ((loc[0] * self.maze.tile_size) + (self.maze.tile_size // 2),  (loc[1] * self.maze.tile_size) + (self.maze.tile_size // 4)), speed=random.uniform(0.1, 0.9))

                # Updates all animations. This isn't done in update display as some logic relies on the animation states
                AnimationHandler.update(self.dt)

                # Moves spikes
                for spike in self.spikes:
                    spike.update()
                    if spike.speed <= 0:
                        self.spikes.remove(spike)

                # Updates the player and the enemies if the player isn't dead
                if not self.player.animation.current_animation == "death":
                    self.player.update()
                    for enemy in self.enemies:
                        enemy.update()

                # Ends the game if the player's death animation is over
                elif self.player.animation.done:
                    self.game_over = True
                    AudioPlayer.play_sound("game_over")
                    data = load_data()
                    update_scores((data['logged_in'], self.gold))

                self.treasure.update()

                # Calculates the camera displacement
                self.camera_displacement[0] = int(self.player.pos[0] - (self.display.get_width() // 2))
                self.camera_displacement[1] = int(self.player.pos[1] - (self.display.get_height() // 2))

            # Decrements the transition timer and draws the transition   
            self.transition_timer = min(self.transition_timer + self.dt, TRANSITION_DURATION)

            # Ends the screen if the transition is over
            if self.transition_timer >= 0 and (self.game_over or self.paused) and self.end_transition:
                self.kill_screen = True

            self.handle_events()
            self.update_display()
            self.clock.tick(self.fps)

        # Kills all animations, particles and sounds and then returns to the main menu once the game loop has finished
        for particle in ParticleHandler.particles.copy():
            ParticleHandler.kill_particle(particle)
        for animation in AnimationHandler.animations.copy():
            AnimationHandler.kill_animation(animation)
        pygame.mixer.stop()
        return "main_menu"