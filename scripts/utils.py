import pygame
import os

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
        filename = f"img_{i}.png"
        if filename in filenames:
            img = load_image(f"{path}/{filename}")
            images.append(img)
    return images

def get_text_surf(size, text, colour, bold=False, italic=False, underline=False):
    """
    Writes text to a surface
    """
    font = pygame.font.Font("assets/font.ttf", size)
    font.set_bold(bold)
    font.set_italic(italic)
    font.set_underline(underline)
    text_surf = font.render(text, False, colour).convert_alpha()
    return text_surf

def format_num(num):
    """
    Formats numbers
    """
    result = str(num)
    data = (("QT", 18), ("Q", 15), ("T", 12), ("B", 9), ("M", 6), ("k", 3))
    for value in data:
        if num >= 10 ** value[1]:
            result = str(round(num / 10 ** value[1], 1)) + value[0]
    return result

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
    pygame.display.init()
    window = pygame.display.set_mode(resolution)
    pygame.mouse.set_visible(False)
    pygame.display.set_caption("Treasure Trove - Options Menu")
    pygame.display.set_icon(load_image("assets/images/icon.png"))
    return window