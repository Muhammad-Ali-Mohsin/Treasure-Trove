import os
import re
import random
import json
import hashlib
import math

import pygame

from scripts.shaders.window import MGLWindow

DATA_PATH = "assets/data.json"
IMG_NAME = "img"
FONT_PATH = "assets/font.ttf"

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
    img_count = len([*filter(lambda filename: filename[-4:] == ".png", os.listdir(path))])
    filenames = os.listdir(path)
    images = []
    for i in range(img_count):
        filename = f"{IMG_NAME}_{i}.png"
        if filename in filenames:
            img = load_image(f"{path}/{filename}")
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
    if displacement[0] == 0 or displacement[1] == 0:
        displacement = (random.choice(-1, 1), random.choice(-1, 1))

    magnitude = math.sqrt((displacement[0] ** 2) + (displacement[1] ** 2))

    # Creates a vector of magnitude 'speed' by multiplying each component by speed/magnitude
    vector = (displacement[0] * (speed/magnitude), displacement[1] * (speed/magnitude))

    return vector

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
            sound = pygame.mixer.Sound(path + '/' + filename)
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

