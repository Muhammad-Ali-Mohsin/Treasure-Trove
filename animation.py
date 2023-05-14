import os
import pygame

class Animation:
    def __init__(self):
        """
        Creates the intial variables
        """
        self.timer = 0
        self.frame = 0
        self.current_animation = None
        self.animation_library = {}
        self.flipped = False

    def load_animation(self, animation_name, path, times):
        """
        Loads an animation from a given path and adds it to the animation library with a given name and frame timings
        """
        # Creates a list of all the frames
        frames = os.listdir(path)
        frames.remove("times.txt")
        animation = []
        
        # Loads each frame into a pygame image and adds it to the list with its corresponding time
        for num, frame in enumerate(frames):
            img = pygame.image.load(f"{path}/{frame}").convert_alpha()
            animation.append((img, times[num]))

        # Adds the animation to the animation library as a tuple
        self.animation_library[animation_name] = tuple(animation)

    def load_animations(self, animations_path):
        """
        Loads multiple animations from a path containing a list of folders each containing the timings and named the animation name
        """
        # List of the animations
        animations = os.listdir(animations_path)
        # Loads each animation with their corresponding times
        for animation in animations:
            # Loads the animation times
            with open(f"{animations_path}/{animation}/times.txt") as f:
                times = f.read().split(", ")
                for i in range(len(times)): times[i] = float(times[i])
            self.load_animation(animation, f"{animations_path}/{animation}", times)

    def change_animation(self, animation):
        """
        Changes the animation if the new animation exists in the animation library
        """
        # Changes the animation to the new animation if the animation exists in the animatin library
        if animation in self.animation_library:
            self.current_animation = animation
            self.timer = 0
            self.frame = 0

    def tick(self, dt):
        """
        Adds the change in time to the animation timer and changes the frame if needed
        """
        if self.current_animation == None: return 
        # Adds the change in time to the timer
        self.timer += dt
        # Changes the frame to the next frame if the timer has reached the duration of the frame and resets the timer
        if self.timer >= self.animation_library[self.current_animation][self.frame][1]:
            self.timer = 0
            self.frame = (self.frame + 1 )% len(self.animation_library[self.current_animation])

    def draw(self, surface, pos, camera_displacement):
        """
        Draws the animation onto a surface with the camera displacement and flips the image based on the self.flipped value
        """
        if self.current_animation == None: return 
        img = self.animation_library[self.current_animation][self.frame][0]
        surface.blit(pygame.transform.flip(img, flip_x=self.flipped, flip_y=False), (pos[0] - (img.get_width() // 2) - camera_displacement[0], pos[1] - (img.get_height() // 2) - camera_displacement[1]))
        