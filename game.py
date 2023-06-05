import pygame, sys, random
from time import time
from maze import generate_maze
from entities import Player, Enemy
from compass import Compass
from misc import get_text_surf, scale_coord_to_new_res
from map import Map
from animation import Animation
from variables import *

class Treasure:
    def __init__(self, maze):
        self.chest_open_animation = Animation(looped=False)
        self.chest_open_animation.load_animation(animation_name="chest_open", path="assets/animations/chest_open", times=[0.1, 0.5, 0.1, 1])
        self.chest_is_open = False
        self.generate_treasure(maze=maze)
        self.fadeout_timer = 0
        self.opacity = 255
        self.text = get_text_surf(size=30, text="+100 Gold", colour=PRIMARY_COLOUR)
        self.text_timer = 0

    def generate_treasure(self, maze):
        # Finds a random empty cell
        cell = maze.get_random_cell()
        # Places the treasure at that cell
        self.cell = cell

    def open_treasure(self):
        # Starts the chest open animation
        self.chest_open_animation.change_animation("chest_open")
        self.chest_is_open = True
        self.fadeout_timer = 0

    def update(self, maze, dt):
        # Updates the chest fadeout and text position and generates new treasure if the chest has faded out
        if self.chest_is_open and self.chest_open_animation.current_animation == None:
            if self.fadeout_timer >= FADEOUT_TIME:
                self.generate_treasure(maze=maze)
                self.opacity = 255
                self.text_timer = 0
                self.chest_is_open = False
            else:
                self.text_timer += dt * 20
                self.fadeout_timer += dt
                self.opacity = round(((FADEOUT_TIME - self.fadeout_timer) / FADEOUT_TIME) * 255)

    def draw(self, camera_displacement):
        # Draws the chest animation or the chest image
        if self.chest_open_animation.current_animation != None:
            pos = (self.cell[0] * CELL_SIZE + 2 * (CHEST_IMG.get_width() // 2), self.cell[1] * CELL_SIZE + 2 * (CHEST_IMG.get_height() // 2))
            self.chest_open_animation.draw(MAZE_SURFACE, pos=pos, camera_displacement=camera_displacement)
        else:
            pos = (self.cell[0] * CELL_SIZE - camera_displacement[0] + (CHEST_IMG.get_width() // 2), self.cell[1] * CELL_SIZE - camera_displacement[1] + (CHEST_IMG.get_height() // 2))
            img = CHEST_IMG.copy()
            img.set_alpha(self.opacity)
            MAZE_SURFACE.blit(img, pos)



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
        self.moving = {'left': False, 'right': False, 'up': False, 'down': False}
        self.compass = Compass()
        self.gold = 0
        self.game_over = False
        self.paused = False
        self.map_open = False
        self.map = Map()
        self.enemies = []

        # Maze Variables
        self.maze = generate_maze()
        self.treasure = Treasure(maze=self.maze)

        # Finds Random Spawning Cell
        cell = self.maze.get_random_cell()
        # Creates a Player in that cell
        self.player = Player(x=cell[0] * CELL_SIZE + (CELL_SIZE // 2), y=cell[1] * CELL_SIZE + (CELL_SIZE // 2))
        self.player.animation.change_animation(animation="idle_forwards")

    def update_display(self):
        """
        Updates the screen
        """
        SCREEN.fill((255, 255, 255))
        MAZE_SURFACE.fill((0, 0, 0))

        # Draws the maze
        self.maze.draw(surface=MAZE_SURFACE, camera_displacement=self.camera_displacement)

        # Draws the treasure
        self.treasure.draw(camera_displacement=self.camera_displacement)

        # Draws the player
        self.player.animation.draw(MAZE_SURFACE, self.player.rect.center, self.camera_displacement)

        # Draws the enemies
        for enemy in self.enemies:
            enemy.animation.draw(MAZE_SURFACE, enemy.rect.center, self.camera_displacement)             

        # Scales the maze surface and blits it onto the screen
        SCREEN.blit(pygame.transform.scale(MAZE_SURFACE, GAME_RESOLUTION), (0, 0))

        # Draws the +100 gold text above the treasure if it's being opened
        if self.treasure.text_timer != 0:
            self.treasure.text.set_alpha(self.treasure.opacity)
            pos = (self.treasure.cell[0] * CELL_SIZE - self.camera_displacement[0] + CELL_SIZE // 2, self.treasure.cell[1] * CELL_SIZE - self.camera_displacement[1] - self.treasure.text_timer)
            pos = scale_coord_to_new_res(coord=pos, old_resolution=MAZE_SURFACE_RESOLUTION, new_resolution=GAME_RESOLUTION)
            SCREEN.blit(self.treasure.text, (pos[0] - (self.treasure.text.get_width() // 2), pos[1]))
        
        #Draws the Compass
        self.compass.draw()

        # Draws the map if it's open
        if self.map_open:
            self.map.draw(player_pos=self.player.rect.center)

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
                    self.moving['left'] = True
                if event.key == pygame.K_RIGHT:
                    self.moving['right'] = True
                if event.key == pygame.K_DOWN:
                    self.moving['down'] = True
                if event.key == pygame.K_UP:
                    self.moving['up'] = True
                if event.key == pygame.K_e:
                    self.player.attack()
                if event.key == pygame.K_TAB:
                    self.paused = not self.paused
                if event.key == pygame.K_m:
                    self.map_open = not self.map_open
                if event.key == pygame.K_1:
                    self.spawn_enemy()
                if event.key == pygame.K_BACKSPACE:
                    self.selected_screen = "main menu"

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.moving['left'] = False
                if event.key == pygame.K_RIGHT:
                    self.moving['right'] = False
                if event.key == pygame.K_DOWN:
                    self.moving['down'] = False
                if event.key == pygame.K_UP:
                    self.moving['up'] = False

    def spawn_enemy(self):
        # Finds Random Spawning Cell
        cell = self.maze.get_random_cell()
        # Creates an Enemy in that cell
        enemy = Enemy(x=cell[0] * CELL_SIZE + (CELL_SIZE // 2), y=cell[1] * CELL_SIZE + (CELL_SIZE // 2), )
        enemy.animation.change_animation(animation="idle")
        # Adds the enemy to the enemies list
        self.enemies.append(enemy)
            
    def run_frame(self):
        """
        Runs a frame of the game
        """
        # Calculates the change in time since the last frame
        dt = (time() - self.last_time)
        self.last_time = time()

        if not self.paused:

            # Finds the cell the player is in
            player_cell = self.maze.get_cell(coord=self.player.rect.center)

            # Calculates the camera displacement based on the player's location
            self.camera_displacement[0] = self.player.rect.centerx - (MAZE_SURFACE_RESOLUTION[0] // 2)
            self.camera_displacement[1] = self.player.rect.centery - (MAZE_SURFACE_RESOLUTION[1] // 2)

            
            # Moves the player
            if self.moving['left']:
                self.player.movement[0] -= round(self.player.speed * dt)
            if self.moving['right']:
                self.player.movement[0] += round(self.player.speed * dt)
            if self.moving['up']:
                self.player.movement[1] -= round(self.player.speed * dt)
            if self.moving['down']:
                self.player.movement[1] += round(self.player.speed * dt)
            if self.player.attacking:
                self.player.movement = [0, 0]

            self.player.move(maze=self.maze)
            
            # Moves the enemies to the player
            for enemy in self.enemies:
                enemy.move_to_player(maze=self.maze, dt=dt, player_location=self.player.rect.center)
            
            # Updates the player's attack if they are attacking and opens the chest if they hit the chest
            if self.player.attacking:
                if self.player.update_attack(treasure_cell=self.treasure.cell, dt=dt) == True:
                    if not self.treasure.chest_is_open:
                        self.treasure.open_treasure()
                        self.gold += 100

            # Updates the chest opening if the chest is opening
            if self.treasure.chest_is_open:
                self.treasure.update(maze=self.maze, dt=dt)


            # Finds the bearing between the player and the treasure for the compass
            self.compass.calculate_angle(player_location=player_cell, treasure_location=self.treasure.cell, dt=dt)

            # Updates the Map
            self.map.update_map(maze=self.maze, player_location=self.player.rect.center)

            # Updates all the animations
            Animation.update(dt)

        # Calls functions
        self.handle_events()
        self.update_display()
        clock.tick(self.fps)

