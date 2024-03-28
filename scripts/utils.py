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
        """
        Loads in a sound from a given path and adds it the audio player
        """
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        AudioPlayer.sounds[name] = {'sounds': tuple([sound]), 'shuffle': False, 'current': 0}

    def load_sounds(name, path, volume=1, shuffle=False, overlap=False):
        """
        Loads in a list of sounds from a given directory
        """
        # Lists each individual file audio within the directory
        sounds_list = os.listdir(path)
        sounds = []
        # Creates a sound for each audio file
        for filename in sounds_list:
            sound = pygame.mixer.Sound(os.path.join(path, filename))
            sound.set_volume(volume)
            sounds.append(sound)
        # Adds the list of sounds to the audio player
        AudioPlayer.sounds[name] = {'sounds': tuple(sounds), 'shuffle': shuffle, 'current': 0}
        if overlap:
            AudioPlayer.sounds[name]['overlap'] = True

    def play_sound(sound):
        # Retrieves the sound from the list of sounds
        sound = AudioPlayer.sounds[sound]
        # Checks whether the sound is not current playing, whether it consists of a single audio file or whether it has the overlap flag enabled
        if sound['sounds'][sound['current']].get_num_channels() == 0 or len(sound['sounds']) == 1 or 'overlap' in sound:
            # Calculates the next current sound
            if sound['shuffle']:
                sound['current'] = random.randint(0, len(sound['sounds']) - 1)
            else:
                sound['current'] = (sound['current'] + 1) % len(sound['sounds'])
            # Plays the current sound
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

        # Loads in the shaders
        with open(vert_path, "r") as f:
            vert_shader = f.read()

        with open(frag_path, "r") as f:
            frag_shader = f.read()

        # Program which packages the shaders together
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
            # Checks whether the uniform is a pygame Surface
            if isinstance(uniforms[uniform], pygame.Surface):
                # Converts the uniform to a moderngl Texture
                self.uniforms[uniform] = self.surf_to_texture(uniforms[uniform])
                # Checks whether it has an assigned memory location and if not, assigns it to the next available location
                if uniform not in self.memory_locations:
                    if len(self.memory_locations) == 0:
                       self.memory_locations[uniform] = 0
                    else: 
                        self.memory_locations[uniform] = max(self.memory_locations.values()) + 1
                    # Tells the program which memory location the uniform is at
                    self.program[uniform] = self.memory_locations[uniform]
                # Tells the uniform which memory location to go to
                self.uniforms[uniform].use(self.memory_locations[uniform])
            else:
                self.program[uniform].value = uniforms[uniform]

    def release(self, uniforms={}):
        """
        Releases all the uniforms to free the space in memory
        """
        for uniform in uniforms:
            # Checks if the uniform is a moderngl Texture and releases it if so
            if uniform in self.uniforms and isinstance(self.uniforms[uniform], moderngl.Texture):
                    self.uniforms[uniform].release()

    def surf_to_texture(self, surf):
        """
        Converts a pygame surface to an OpenGL texture
        """
        # Creates a texture the same size as the surface
        tex = self.ctx.texture(surf.get_size(), 4)
        # Tells the texture to use the nearest colour when resizing instead of interpolating colours
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        # Tells te texture to use the BGRA format that pygame uses instead of the conventional RGBA
        tex.swizzle = 'BGRA'
        # Fills the texture with the pixel data from the pygame surface
        tex.write(surf.get_view('1'))
        return tex

    def update(self, uniforms={}):
        """
        Updates the display when provided with the uniforms
        """
        # Passes the uniforms to te program and then runs the shaders to render the frame before releasing the uniforms and updating the screen
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
    # Finds all the files in the folder ending in .png
    filenames = [*filter(lambda filename: filename.endswith('.png'), os.listdir(path))]
    img_count = len(filenames)
    images = []
    # Loops as many times as there are images in the folder
    for i in range(img_count):
        # Reconstructs the filename and loads the image in. This makes sure the images load correctly in order of their number.
        filename = f"{IMG_NAME}_{i}.png"
        if filename in filenames:
            img = load_image(os.path.join(path, filename))
            images.append(img)
    return images

def load_data():
    # Checks whether the data exists and returns it if so or returns a default set of data if it doesn't
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH ,"r") as f:
            data = json.load(f)
    else:
        data = {'scores': [], 'accounts': {}, 'options': {'res': None, 'fps': 60}}
    return data

def save_data(data):
    # Takes the data and saves it to the file
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

def get_hash(text):
    # Uses the SHA-256 hashing algorithm to hash given text
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
    # Divides the new resolution by the old to calculate a scale and ten multiplies te coordinates by the scale
    return (coord[0] * new_resolution[0] / old_resolution[0], coord[1] * new_resolution[1] / old_resolution[1])

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
    # Calculates the displacement between the two given points
    displacement = (coords[0][0] - coords[1][0], coords[0][1] - coords[1][1])

    # Makes the displacement a random direction if the displacement 0 so that the magnitude can't be 0
    if displacement[0] == 0 and displacement[1] == 0:
        displacement = (random.choice((-1, 1)), random.choice((-1, 1)))

    # Calculates the magnitude using pythagoras'
    magnitude = math.sqrt((displacement[0] ** 2) + (displacement[1] ** 2))

    # Creates a vector of magnitude 'speed' by multiplying each component by speed/magnitude
    vector = (displacement[0] * (speed/magnitude), displacement[1] * (speed/magnitude))

    return vector