import os
import re
import random
import json
import hashlib
import math
import moderngl

import pygame

from array import array

DATA_PATH = "assets/data.json"
IMG_NAME = "img"
FONT_PATH = "assets/font.ttf"

class AudioPlayer:
    sounds = {}

    def load_sound(name, path, volume=1):
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        AudioPlayer.sounds[name] = {'sounds': tuple([sound]), 'shuffle': False, 'current': 0}

    def load_sounds(name, path, volume=1, shuffle=False, overlap=False):
        sounds_list = os.listdir(path)
        sounds = []
        for filename in sounds_list:
            sound = pygame.mixer.Sound(os.path.join(path, filename))
            sound.set_volume(volume)
            sounds.append(sound)
        AudioPlayer.sounds[name] = {'sounds': tuple(sounds), 'shuffle': shuffle, 'current': 0}
        if overlap:
            AudioPlayer.sounds[name]['overlap'] = True

    def play_sound(sound):
        sound = AudioPlayer.sounds[sound]
        if sound['sounds'][sound['current']].get_num_channels() == 0 or len(sound['sounds']) == 1 or 'overlap' in sound:
            if sound['shuffle']:
                sound['current'] = random.randint(0, len(sound['sounds']) - 1)
            else:
                sound['current'] = (sound['current'] + 1) % len(sound['sounds'])
            sound['sounds'][sound['current']].play()

    def stop_sound(sound):
        AudioPlayer.sounds[sound]['sounds'][AudioPlayer.sounds[sound]['current']].stop()

class MGLWindow:
    def __init__(self, vert_path, frag_path, resolution):
        self.window = pygame.display.set_mode(resolution, pygame.OPENGL | pygame.DOUBLEBUF)
        self.ctx = moderngl.create_context()
        self.uniforms = {}
        self.memory_locations = {}

        # Vertex Buffer Object mapping each vertice on the pygame surface to the one on the opengl texture. Each line is (mgl x, mgl y, py x, py y)
        vbo = self.ctx.buffer(data=array('f', [
            -1.0, 1.0, 0.0, 0.0,
            1.0, 1.0, 1.0, 0.0,
            -1.0, -1.0, 0.0, 1.0,
            1.0, -1.0, 1.0, 1.0,
        ]))

        with open(vert_path, "r") as f:
            vert_shader = f.read()

        with open(frag_path, "r") as f:
            frag_shader = f.read()

        self.program = self.ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)

        # Vertex Array Object
        self.vao = self.ctx.vertex_array(self.program, [(vbo, '2f 2f', 'vert', 'texcoord')])

        # Creates a texture for the noise used for the shadow border
        noise = pygame.image.load("assets/images/noise.png").convert_alpha()
        self.pass_uniforms({'noise_texture': noise})

    def pass_uniforms(self, uniforms={}):
        """
        Turns all the surface uniforms into textures and passes them into the vao
        """
        for uniform in uniforms:
            if isinstance(uniforms[uniform], pygame.Surface):
                self.uniforms[uniform] = self.surf_to_texture(uniforms[uniform])
                if uniform not in self.memory_locations:
                    if len(self.memory_locations) == 0:
                       self.memory_locations[uniform] = 0
                    else: 
                        self.memory_locations[uniform] = max(self.memory_locations.values()) + 1
                    self.program[uniform] = self.memory_locations[uniform]
                self.uniforms[uniform].use(self.memory_locations[uniform])
            else:
                self.program[uniform].value = uniforms[uniform]

    def release(self, uniforms={}):
        """
        Releases all the uniforms to free the space in memory
        """
        for uniform in uniforms:
            if uniform in self.uniforms and isinstance(self.uniforms[uniform], moderngl.Texture):
                    self.uniforms[uniform].release()

    def surf_to_texture(self, surf):
        """
        Converts a pygame surface to an OpenGL texture
        """
        # Creates a texture the same size as the surface and fills it with data from the surface
        tex = self.ctx.texture(surf.get_size(), 4)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.swizzle = 'BGRA'
        tex.write(surf.get_view('1'))
        return tex

    def update(self, uniforms={}):
        """
        Updates the display when provided with the uniforms
        """
        self.pass_uniforms(uniforms)
        self.vao.render(mode=moderngl.TRIANGLE_STRIP)
        self.release(uniforms)
        pygame.display.flip()

    def get_size(self):
        return self.window.get_size()

    def get_height(self):
        return self.window.get_height()

    def get_width(self):
        return self.window.get_width()

def load_image(path):
    """
    Loads an image from a specified path
    """
    img = pygame.image.load(path).convert_alpha()
    return img

def load_images(path):
    """
    Loads all the image within a specified folder
    """
    filenames = [*filter(lambda filename: filename[-4:] == ".png", os.listdir(path))]
    img_count = len(filenames)
    images = []
    for i in range(img_count):
        filename = f"{IMG_NAME}_{i}.png"
        if filename in filenames:
            img = load_image(os.path.join(path, filename))
            images.append(img)
    return images

def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH ,"r") as f:
            data = json.load(f)
    else:
        data = {'scores': [], 'accounts': {}, 'options': {'res': None, 'fps': 60}}
    return data

def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

def get_hash(text):
    sha256 = hashlib.sha256()
    sha256.update(str.encode(text))
    return sha256.hexdigest()

def update_scores(score):
    """
    Takes a score and updates the high scores file using an insertion sort
    """
    # Loads the scores and adds the new score
    data = load_data()
    high_scores = data['scores']
    high_scores.append(score)

    # Sorts the scores
    for i in range(len(high_scores)):
        index = i
        while index != 0 and high_scores[i][1] > high_scores[index - 1][1]:
            index = index - 1
        score = high_scores.pop(i)
        high_scores.insert(index, score)
    
    # Saves the scores
    data['scores'] = high_scores[:10]
    save_data(data)

def get_text_surf(size, text, colour, font=None, bold=False, italic=False, underline=False):
    """
    Writes text to a surface
    """
    if font == None:
        font = pygame.font.Font(FONT_PATH, size)
    font.set_bold(bold)
    font.set_italic(italic)
    font.set_underline(underline)
    text_surf = font.render(text, False, colour).convert_alpha()
    return text_surf

def format_num(num):
    """
    Formats numbers with a comma
    """
    return re.sub("(?<=\d)(?=(\d{3})+(?!\d))", ",", str(num))

def scale_coord_to_new_res(coord, old_resolution, new_resolution):
    """
    Maps a coordinate onto the the corresponding point on a new resolution
    """
    x_scale = new_resolution[0] / old_resolution[0]
    y_scale = new_resolution[1] / old_resolution[1]
    x = coord[0] * x_scale
    y = coord[1] * y_scale
    return (x, y)

def create_window(resolution):
    """
    Creates a window
    """
    pygame.display.init()
    window = MGLWindow("scripts/shaders/shader.vert", "scripts/shaders/shader.frag", resolution)
    pygame.mouse.set_visible(False)
    pygame.display.set_icon(load_image("assets/images/icon.png"))
    return window

def get_vector(coords, speed):
    """
    Returns a vector with a certain magnitude between two points
    """
    displacement = (coords[0][0] - coords[1][0], coords[0][1] - coords[1][1])
    if displacement[0] == 0 and displacement[1] == 0:
        displacement = (random.choice((-1, 1)), random.choice((-1, 1)))

    magnitude = math.sqrt((displacement[0] ** 2) + (displacement[1] ** 2))

    # Creates a vector of magnitude 'speed' by multiplying each component by speed/magnitude
    vector = (displacement[0] * (speed/magnitude), displacement[1] * (speed/magnitude))

    return vector