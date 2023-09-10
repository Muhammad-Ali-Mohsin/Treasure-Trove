import pygame
import moderngl

from array import array

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

    def surf_to_texture(self, surf):
        tex = self.ctx.texture(surf.get_size(), 4)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.swizzle = 'BGRA'
        tex.write(surf.get_view('1'))
        return tex
    
    def blit(self, surf, pos):
        self.screen.blit(surf, pos)

    def update(self):
        surf_tex = self.surf_to_texture(self.screen)
        surf_tex.use(0)
        self.program['tex'] = 0
        self.vao.render(mode=moderngl.TRIANGLE_STRIP)
        pygame.display.flip()
        surf_tex.release()

    def get_size(self):
        return self.window.get_size()

    def get_height(self):
        return self.window.get_height()

    def get_width(self):
        return self.window.get_width()    
    