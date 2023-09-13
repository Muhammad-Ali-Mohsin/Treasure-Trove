import pygame
import moderngl

from array import array

def get_daylight(daytime):
    # Defines the color scales for different times
    morning_color = pygame.Vector3(1.0, 0.9, 0.8);
    noon_color = pygame.Vector3(1.0, 1.0, 1.0);
    evening_color = pygame.Vector3(0.9, 0.4, 0.2);
    sunset_color = pygame.Vector3(0.2, 0.2, 0.2);
    night_color = pygame.Vector3(0.1, 0.1, 0.2);
    
    # Interpolates between colors based on time of day
    daylight = 0
    if daytime < 0.2:
        daylight = night_color
    elif daytime < 0.35:
        daylight = ((daytime - 0.2) * (morning_color - night_color) / (0.35 - 0.2)) + night_color
    elif daytime < 0.7:
        daylight = ((daytime - 0.35) * (noon_color - morning_color) / (0.7 - 0.35)) + morning_color
    elif daytime < 0.75:
        daylight = ((daytime - 0.7) * (evening_color - noon_color) / (0.75 - 0.7)) + noon_color
    elif daytime < 0.8:
        daylight = ((daytime - 0.75) * (sunset_color - evening_color) / (0.8 - 0.75)) + evening_color
    else:
        daylight = ((daytime - 0.8) * (night_color - sunset_color) / (1.0 - 0.8)) + sunset_color
    
    return daylight

class MGLWindow:
    def __init__(self, vert_path, frag_path, resolution):
        self.window = pygame.display.set_mode(resolution, pygame.OPENGL | pygame.DOUBLEBUF)
        self.screen = pygame.Surface(resolution)
        self.ctx = moderngl.create_context()

        # Vertex Buffer Object formatted as (mgl x, mgl y, py x, py y)
        # Also known as position (x, y), uv coords (x, y)
        # This maps each vertice on the opengl geometry to the corresponding coordinate on the pygame surface
        vbo = self.ctx.buffer(data=array('f', [
            -1.0, 1.0, 0.0, 0.0,  # Top Left
            1.0, 1.0, 1.0, 0.0,   # Top Right
            -1.0, -1.0, 0.0, 1.0, # Bottom Left
            1.0, -1.0, 1.0, 1.0,  # Bottom Right
        ]))

        with open(vert_path, "r") as f:
            vert_shader = f.read()

        with open(frag_path, "r") as f:
            frag_shader = f.read()

        self.program = self.ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)

        # Vertex Array Object
        self.vao = self.ctx.vertex_array(self.program, [(vbo, '2f 2f', 'vert', 'texcoord')])

        # Creates a texture for the noise used for the shadow border
        noise = pygame.image.load("assets/images/noise.png").convert_alpha()
        self.noise = self.surf_to_texture(noise)
        self.noise.use(2)

        # Assigns memory locations to the uniforms
        self.program['screen_texture'] = 0
        self.program['ldisplay_texture'] = 1
        self.program['noise_texture'] = 2
        self.program['light_map'] = 3

    def surf_to_texture(self, surf):
        # Creates a texture the same size as the surface and fills it with data from the surface
        tex = self.ctx.texture(surf.get_size(), 4)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.swizzle = 'BGRA'
        tex.write(surf.get_view('1'))
        return tex
    
    def blit(self, surf, pos):
        self.screen.blit(surf, pos)

    def update(self, game=None):
        # Retrieves data from the game
        if game == None:
            self.program['screen'] = 1
            screen = self.screen
        else:
            screen = game.display
            self.program['screen'] = 0

            # Converts surfaces to textures
            ldisplay_tex = self.surf_to_texture(game.larger_display)
            light_map_tex = self.surf_to_texture(game.light_map)

            ldisplay_tex.use(1)
            light_map_tex.use(3)

            # Passes uniforms into the shader
            self.program['time'] = game.time
            self.program['daylight'] = get_daylight((game.time / 180) % 1)

        # Passes the actual screen to the shader
        screen_tex = self.surf_to_texture(screen)
        screen_tex.use(0)
        
        # Renders the result
        self.vao.render(mode=moderngl.TRIANGLE_STRIP)

        # Releases the textures from memory
        screen_tex.release()
        if game != None:
            light_map_tex.release()
            ldisplay_tex.release()

        # Updates the display
        pygame.display.flip()

    def get_size(self):
        return self.window.get_size()

    def get_height(self):
        return self.window.get_height()

    def get_width(self):
        return self.window.get_width()    
    