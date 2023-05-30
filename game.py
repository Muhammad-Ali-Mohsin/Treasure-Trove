import pygame, sys, random
from time import time
from maze import generate_maze
from entities import Player, Enemy
from compass import Compass
from variables import *
from misc import get_text_surf
from map import Map


class Game:
    def __init__(self, window, fps):
        """
        Creates all the starting game variables
        """
        # Display Variables
        self.screentype = "game"
        self.selected_screen = "game"
        self.window = window
        self.user_resolution = (window.get_width(), window.get_height())
        self.fps = fps
        random.seed(10)
        
        # Game Variables
        self.last_time = time()
        self.camera_displacement = [0, 0]
        self.movement = {'left': False, 'right': False, 'up': False, 'down': False}
        self.compass = Compass(base_img=COMPASS_BASE_IMG, spinner_img=COMPASS_SPINNER_IMG)
        self.gold = 0
        self.game_over = False
        self.paused = False
        self.map_open = False
        self.map = Map(resolution=MAP_RESOLUTION, maze_resolution=MAZE_RESOLUTION)

        # Maze Variables
        self.maze = generate_maze(x=MAZE_RESOLUTION[0], y=MAZE_RESOLUTION[1], tile_size=TILE_SIZE)
        self.generate_treasure()

        # Finds Random Spawning Cell
        cell = self.maze.get_random_cell()
        # Creates a Player in that cell
        self.player = Player(x=cell[0] * TILE_SIZE + (TILE_SIZE // 2), y=cell[1] * TILE_SIZE + (TILE_SIZE // 2), size=PLAYER_SIZE, speed=PLAYER_SPEED, animations_path="assets/animations/player")
        self.player.animation.change_animation(animation="idle_forwards")

        # Finds Random Spawning Cell
        cell = self.maze.get_random_cell()
        # Creates an Enemy in that cell
        self.enemy = Enemy(x=cell[0] * TILE_SIZE + (TILE_SIZE // 2), y=cell[1] * TILE_SIZE + (TILE_SIZE // 2), size=ENEMY_SIZE, speed=ENEMY_SPEED, animations_path="assets/animations/player", tile_center_size=TILE_CENTER_SIZE, refresh_interval=ENEMY_REFRESH_INTERVAL)
        self.enemy.animation.change_animation(animation="idle_forwards")

    def update_display(self):
        """
        Updates the screen
        """
        SCREEN.fill((255, 255, 255))
        MAZE_SURFACE.fill((0, 0, 0))

        # Draws the maze
        self.maze.draw(MAZE_SURFACE, self.camera_displacement)

        # Draws the treasure
        pygame.draw.rect(MAZE_SURFACE, (255, 255, 0), (self.treasure['cell'][0] * TILE_SIZE - self.camera_displacement[0], self.treasure['cell'][1] * TILE_SIZE - self.camera_displacement[1], TILE_SIZE, TILE_SIZE))

        # Draws the player
        self.player.animation.draw(MAZE_SURFACE, self.player.rect.center, self.camera_displacement)

        # Draws the enemy
        self.enemy.animation.draw(MAZE_SURFACE, self.enemy.rect.center, self.camera_displacement)             

        # Scales the maze surface and blits it onto the screen
        SCREEN.blit(pygame.transform.scale(MAZE_SURFACE, GAME_RESOLUTION), (0, 0))
        
        #Draws the Compass
        self.compass.draw(surface=SCREEN, x=GAME_RESOLUTION[0] - COMPASS_BASE_IMG.get_width() - 20, y=20)

        # Draws the map if it's open
        if self.map_open:
            self.map.draw(surface=SCREEN, pos=((GAME_RESOLUTION[0] // 2) - (MAP_RESOLUTION[0] // 2), (GAME_RESOLUTION[1] // 2) - (MAP_RESOLUTION[1] // 2)), player_pos=self.player.rect.center)

        if self.paused:
            # Draws the pause box and pause text
            SCREEN.blit(PAUSE_SCREEN_BOX_IMG, ((GAME_RESOLUTION[0] // 2) - (PAUSE_SCREEN_BOX_IMG.get_width() // 2), (GAME_RESOLUTION[1] // 2) - (PAUSE_SCREEN_BOX_IMG.get_height() // 2)))
            pause_text = get_text_surf(size=80, text="Paused", colour=PRIMARY_COLOUR)
            SCREEN.blit(pause_text, ((GAME_RESOLUTION[0] // 2) - (pause_text.get_width() // 2), (GAME_RESOLUTION[1] // 2) - 170))

             # Writes all the stats to the pause screen
            for i, data in enumerate([["Gold", str(self.gold)], ["Lives", "69"], ["Name", "Bob"]]):
                text_surf = get_text_surf(size=50, text=data[0], colour=PRIMARY_COLOUR)
                SCREEN.blit(text_surf, ((GAME_RESOLUTION[0] // 2) - (PAUSE_SCREEN_BOX_IMG.get_width() // 2) + 50, (i * 50) + (GAME_RESOLUTION[1] // 2) - 75))
                text_surf = get_text_surf(size=50, text=data[1], colour=PRIMARY_COLOUR)
                SCREEN.blit(text_surf, ((GAME_RESOLUTION[0] // 2) + (PAUSE_SCREEN_BOX_IMG.get_width() // 2) - (text_surf.get_width()) - 50, (i * 50) + (GAME_RESOLUTION[1] // 2) - 75))

            prompt_text = get_text_surf(size=30, text=f"Press Backspace to return to Main Menu", colour=pygame.Color("white"))
            SCREEN.blit(prompt_text, ((GAME_RESOLUTION[0] // 2) - (prompt_text.get_width() // 2), (GAME_RESOLUTION[1] // 2) + 125))

        #Shows the FPS
        fps_text = get_text_surf(size=55, text=f"FPS: {round(clock.get_fps())}", colour=pygame.Color("white"))
        SCREEN.blit(fps_text, (10, 10))

        # Ouputs the display in the user resolution
        self.window.blit(pygame.transform.scale(SCREEN, self.user_resolution), (0, 0))
        pygame.display.update()

    def handle_events(self):
        """
        Handles all input events such as key presses
        """
        for event in pygame.event.get():
            # Checks whether the X button has been pressed
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_LEFT:
                    self.movement['left'] = True
                if event.key == pygame.K_RIGHT:
                    self.movement['right'] = True
                if event.key == pygame.K_DOWN:
                    self.movement['down'] = True
                if event.key == pygame.K_UP:
                    self.movement['up'] = True
                if event.key == pygame.K_e:
                    self.dig()
                if event.key == pygame.K_TAB:
                    self.paused = not self.paused
                if event.key == pygame.K_m:
                    self.map_open = not self.map_open
                if event.key == pygame.K_BACKSPACE:
                    self.selected_screen = "main menu"

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.movement['left'] = False
                if event.key == pygame.K_RIGHT:
                    self.movement['right'] = False
                if event.key == pygame.K_DOWN:
                    self.movement['down'] = False
                if event.key == pygame.K_UP:
                    self.movement['up'] = False

    def generate_treasure(self):
        """
        Generates treasure on a random cell in the maze
        """
        # Finds a random empty cell
        cell = self.maze.get_random_cell()
        # Places the treasure at that cell
        self.treasure = {'cell': cell, 'dig_counter': 0}

    def dig(self):
        """
        Attempts to dig for treasure at the player's current cell
        """
        # Checks whether the dig is successfull (whether there is treasure there or not)
        success = self.player.dig(treasure=self.treasure, tile_size=TILE_SIZE)
        if success:
            self.treasure['dig_counter'] += 1
            # If the player has dug 3 times to fully uncover the treasure
            if self.treasure['dig_counter'] == 3:
                # Generate new treausre
                self.generate_treasure()
                # Give the player 100 gold
                self.gold += 100
        else:
            pass

    def change_player_animation(self):
        """
        Changes the player's animation based on their movements
        """
        if self.movement['left']:
            self.player.animation.change_animation(animation="running_sideways") if self.player.animation.current_animation != "running_sideways" else None
            self.player.animation.flipped = True
        elif self.movement['right']:
            self.player.animation.change_animation(animation="running_sideways") if self.player.animation.current_animation != "running_sideways" else None
            self.player.animation.flipped = False
        elif self.movement['up'] and self.player.animation.current_animation != "running_backwards":
            self.player.animation.change_animation(animation="running_backwards")
        elif self.movement['down'] and self.player.animation.current_animation != "running_forwards":
            self.player.animation.change_animation(animation="running_forwards")
        elif not self.movement['left'] and not self.movement['right'] and not self.movement['up'] and not self.movement['down'] and ("idle" not in self.player.animation.current_animation):
            if self.player.animation.current_animation == "running_sideways":
                self.player.animation.change_animation(animation="idle_sideways")
            elif self.player.animation.current_animation == "running_backwards":
                self.player.animation.change_animation(animation="idle_backwards")
            else:
                self.player.animation.change_animation(animation="idle_forwards")
            
    def run_frame(self):
        """
        Runs a frame of the game
        """
        # Calculates the change in time since the last frame
        dt = (time() - self.last_time)
        self.last_time = time()

        if not self.paused:

            # Finds the cell the player is in
            player_cell = (self.player.rect.centerx // TILE_SIZE, self.player.rect.centery // TILE_SIZE)

            # Calculates the camera displacement based on the player's location
            self.camera_displacement[0] = self.player.rect.centerx - (MAZE_SURFACE_RESOLUTION[0] // 2)
            self.camera_displacement[1] = self.player.rect.centery - (MAZE_SURFACE_RESOLUTION[1] // 2)

            # Moves the player
            self.player.move(movement=self.movement, maze=self.maze, tile_size=TILE_SIZE, dt=dt)

            # Moves the Enemy
            self.enemy.move_to_player(maze=self.maze, tile_size=TILE_SIZE, dt=dt, player_location=self.player.rect.center)

            # Finds the bearing between the player and the treasure for the compass
            self.compass.calculate_angle(player_location=player_cell, treasure_location=self.treasure['cell'], dt=dt)

            # Updates the Map
            self.map.update_map(maze=self.maze, player_location=self.player.rect.center, tile_size=TILE_SIZE)

            # Updates animations
            self.player.animation.tick(dt=dt)
            self.enemy.animation.tick(dt=dt)


        # Calls functions
        self.handle_events()
        self.update_display()
        clock.tick(self.fps)

