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
    text_surf = font.render(text, True, colour)
    return text_surf