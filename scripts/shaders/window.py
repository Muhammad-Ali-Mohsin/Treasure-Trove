import pygame
import moderngl

from array import array

class MGLWindow:
    def __init__(self, vert_path, frag_path, resolution):
        self.window = pygame.display.set_mode(resolution, pygame.OPENGL | pygame.DOUBLEBUF)
        self.screen = pygame.Surface(resolution)
        self.ctx = moderngl.create_context()
        self.uniforms = {}
        self.memory_locations = {}

        # Vertex Buffer Object mapping each vertice on the pygame surface to the one on the opengl texture. Each line is (mgl x, mgl y, py x, py y)
        vbo = self.ctx.buffer(data=array('f', [
            -1.0, 1.0, 0.0, 0.0,
            1.0, 1.0, 1.0, 0.0,
            -1.0, -1.0, 0.0, 1.0,
            1.0, -1.0, 1.0, 1.0,
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
        self.pass_uniforms({'noise_texture': noise})

    def pass_uniforms(self, uniforms={}):
        """
        Turns all the surface uniforms into textures and passes them into the vao
        """
        for uniform in uniforms:
            if isinstance(uniforms[uniform], pygame.Surface):
                self.uniforms[uniform] = self.surf_to_texture(uniforms[uniform])
                if uniform not in self.memory_locations:
                    if len(self.memory_locations) == 0:
                       self.memory_locations[uniform] = 0
                    else: 
                        self.memory_locations[uniform] = max(self.memory_locations.values()) + 1
                    self.program[uniform] = self.memory_locations[uniform]
                self.uniforms[uniform].use(self.memory_locations[uniform])
            else:
                self.program[uniform].value = uniforms[uniform]

    def release(self, uniforms={}):
        """
        Releases all the uniforms to free the space in memory
        """
        for uniform in uniforms:
            if uniform in self.uniforms and isinstance(self.uniforms[uniform], moderngl.Texture):
                    self.uniforms[uniform].release()

    def surf_to_texture(self, surf):
        """
        Converts a pygame surface to an OpenGL texture
        """
        # Creates a texture the same size as the surface and fills it with data from the surface
        tex = self.ctx.texture(surf.get_size(), 4)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.swizzle = 'BGRA'
        tex.write(surf.get_view('1'))
        return tex

    def update(self, uniforms={}):
        """
        Updates the display when provided with the uniforms
        """
        self.pass_uniforms(uniforms)
        self.vao.render(mode=moderngl.TRIANGLE_STRIP)
        self.release(uniforms)
        pygame.display.flip()

    def blit(self, *args, special_flags=0):
        """
        Blits onto the an internal surface allowing the OpenGL window to be treated like a Pygame Window
        """
        self.screen.blit(*args, special_flags=special_flags)

    def get_size(self):
        return self.window.get_size()

    def get_height(self):
        return self.window.get_height()

    def get_width(self):
        return self.window.get_width()    
    