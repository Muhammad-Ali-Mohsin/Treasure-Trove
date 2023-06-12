import pygame, os, random

class Audio:
    def __init__(self, sounds, shuffle):
        self.sounds = sounds
        self.shuffle = shuffle
        self.current_sound = 0

class AudioPlayer:
    audios = {}

    def load_sound(name, path, volume=1):
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        AudioPlayer.audios[name] = Audio(sounds=[sound], shuffle=False)

    def load_sounds(name, path, volume=1, shuffle=False):
        sounds_list = os.listdir(path)
        sounds = []
        for sound in sounds_list:
            sound = pygame.mixer.Sound(os.path.join(path, sound))
            sound.set_volume(volume)
            sounds.append(sound)
        AudioPlayer.audios[name] = Audio(sounds=sounds, shuffle=shuffle)

    def play_sound(sound):
        current_sound = AudioPlayer.audios[sound].sounds[AudioPlayer.audios[sound].current_sound]
        if current_sound.get_num_channels() == 0:
            if AudioPlayer.audios[sound].shuffle == False:
                AudioPlayer.audios[sound].current_sound = (AudioPlayer.audios[sound].current_sound + 1) % len(AudioPlayer.audios[sound].sounds)
            else:
                AudioPlayer.audios[sound].current_sound = random.randint(0, len(AudioPlayer.audios[sound].sounds) - 1)
            AudioPlayer.audios[sound].sounds[AudioPlayer.audios[sound].current_sound].play()

    def stop_sound(sound):
        AudioPlayer.audios[sound].sounds[AudioPlayer.audios[sound].current_sound].stop()


def get_text_surf(size, text, colour, bold=False, italic=False, underline=False):
    """
    Writes text to a surface
    """
    font = pygame.font.Font("assets/font.ttf", size)
    font.set_bold(bold)
    font.set_italic(italic)
    font.set_underline(underline)
    text_surf = font.render(text, True, colour)
    return text_surf

def get_mouse_pos(old_resolution, new_resolution):
    """
    Returns the mouse position translated from the user's resolution to a new resolution
    """
    return scale_coord_to_new_res(pygame.mouse.get_pos(), old_resolution, new_resolution)

def get_options():
    """
    Returns the data from the options file
    """
    if os.path.exists("assets/options.txt"):
        # Loads the data from the options file
        with open("assets/options.txt", "r") as file:
            options = file.readlines()
        for i in range(len(options)):
            options[i] = options[i].split("=")[1].strip()

        # Converts the resolution to a tuple
        user_resolution = options[0].split("x")
        user_resolution = (int(user_resolution[0]), int(user_resolution[1]))
        fps = int(options[1])

        return user_resolution, fps
    
def get_scores():
    """
    Returns the scores from the scores file
    """
    if os.path.exists("assets/scores.txt"):
        # Loads the data from the scores file
        with open("assets/scores.txt", "r") as file:
            scores = file.readlines()
        # Converts the scores to an integer and returns the list
        scores = map(lambda score: int(score.strip()), scores)
        return scores
    
def update_options(user_resolution, fps):
    options = f"USER_RESOLUTION={user_resolution[0]}x{user_resolution[1]}\nFPS={fps}"
    with open("assets/options.txt", "w") as file:
        file.write(options)

def scale_coord_to_new_res(coord, old_resolution, new_resolution):
    """
    Maps a coordinate onto the the corresponding point on a new resolution
    """
    x_scale = new_resolution[0] / old_resolution[0]
    y_scale = new_resolution[1] / old_resolution[1]
    x = coord[0] * x_scale
    y = coord[1] * y_scale
    return (x, y)
