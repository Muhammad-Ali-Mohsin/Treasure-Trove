import pygame

class Node():
    """
    Node used in the enemy pathfinding algorithm
    """
    def __init__(self, cell, parent):
        self.cell = cell
        self.parent = parent


class QueueFrontier():
    """
    Queue Frontier used in the enemy pathfinding algorithm
    """
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_cell(self, cell):
        return any(node.cell == cell for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("Empty Frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node
        
def get_text_surf(size, text, colour, bold=False, italic=False, underline=False):
    """
    Writes text to a surface
    """
    font = pygame.font.Font("assets/font.ttf", size)
    font.set_bold(bold)
    font.set_italic(italic)
    font.set_underline(underline)
    text_surf = font.render(text, 1, colour)
    return text_surf

def get_mouse_pos(user_resolution, new_resolution):
    """
    Returns the mouse position translated from the user's resolution to a new resolution
    """
    x, y = pygame.mouse.get_pos()
    x_scale = new_resolution[0] / user_resolution[0]
    y_scale = new_resolution[1] / user_resolution[1]
    x *= x_scale
    y *= y_scale
    return x, y