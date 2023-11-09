import os

import pygame

from scripts.utils import load_images

def load_animation(path, times, looped):
    """
    Loads an animation from a given path and returns it
    """
    images = load_images(path)
    return {'images': images, 'times': times, 'looped': looped}

def load_animation_library(animations_path):
    """
    Loads an animation library from a given path and returns it
    This treats each folder in the given path as an individual animation and expects a data.txt file to store the times and loop status for each animation
    """
    # List of the animations
    animations = os.listdir(animations_path)
    library = {}
    # Loads each animation with their corresponding times
    for animation in animations:
        # Loads the animation times
        with open(f"{animations_path}/{animation}/data.txt") as f:
            times = tuple(map(lambda time: float(time), f.readline().split(", ")))
            looped = bool(int(f.readline()))
        library[animation] = load_animation(f"{animations_path}/{animation}", times, looped)
    
    return library


class AnimationHandler:
    animations = []

    def update(dt):
        """
        Adds the change in time to the animation timer and changes the frame if needed for all animations
        """
        for animation in AnimationHandler.animations:
            if animation.current_animation == None or animation.done == True: continue 
            # Adds the change in time to the timer
            animation.timer += dt
            # Changes the frame to the next frame if the timer has reached the duration of the frame and resets the timer
            if animation.timer >= animation.animation_library[animation.current_animation]['times'][animation.frame]:
                animation.timer = 0
                if animation.animation_library[animation.current_animation]['looped'] or animation.frame + 1 < len(animation.animation_library[animation.current_animation]['images']):
                    new_frame = (animation.frame + 1) % len(animation.animation_library[animation.current_animation]['images'])
                    animation.frame = new_frame
                else:
                    animation.done = True

    def create_animation():
        """
        Returns a new animation
        """
        animation = AnimationManager()
        AnimationHandler.animations.append(animation)
        return animation

    def kill_animation(animation):
        """
        Removes an animation from the animations list
        """
        AnimationHandler.animations.remove(animation)


class AnimationManager:
    def __init__(self):
        self.timer = 0
        self.frame = 0
        self.current_animation = "default"
        self.animation_library = {}
        self.flip = False
        self.done = False

    def change_animation_library(self, animation_library):
        """
        Changes the animation library
        """
        self.animation_library = animation_library

    def change_animation(self, animation):
        """
        Changes the animation if the new animation exists in the animation library and the new animation is not the current animation
        """
        # Changes the animation to the new animation if the animation exists in the animation library
        if animation in self.animation_library and self.current_animation != animation:
            self.current_animation = animation
            self.timer = 0
            self.frame = 0
            self.done = False

    def get_img(self):
        """
        Returns the current animation image
        """
        return pygame.transform.flip(self.animation_library[self.current_animation]['images'][self.frame], flip_x=self.flip, flip_y=False)
        
        