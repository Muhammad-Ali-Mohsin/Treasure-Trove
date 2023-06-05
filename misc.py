import pygame, os
        
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
