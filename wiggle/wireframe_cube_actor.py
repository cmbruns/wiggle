from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram

from .renderer import AutoInitRenderer
from .matrix import ModelMatrix


class WireframeCubeActor(AutoInitRenderer):
    """
    Draws a cube
    
       2________ 3
       /|      /|
     6/_|____7/ |
      | |_____|_| 
      | /0    | /1
      |/______|/
      4       5
    """
    
    def __init__(self):
        super().__init__()
        self.shader = 0
        self.model_matrix = ModelMatrix()
    
    def init_gl(self):
        vertex_shader = compileShader(
            """#version 430
            // Adapted from @jherico's RiftDemo.py in pyovr
            
            layout(location = 0) uniform mat4 Projection = mat4(1);
            layout(location = 4) uniform mat4 ModelView = mat4(1);
            
            const float r = 0.5;
            
            const vec3 CUBE_VERTICES[8] = vec3[8](
              vec3(-r, -r, -r), // 0: lower left rear
              vec3(+r, -r, -r), // 1: lower right rear
              vec3(-r, +r, -r), // 2: upper left rear
              vec3(+r, +r, -r), // 3: upper right rear
              vec3(-r, -r, +r), // 4: lower left front
              vec3(+r, -r, +r), // 5: lower right front
              vec3(-r, +r, +r), // 6: upper left front
              vec3(+r, +r, +r)  // 7: upper right front
            );
            
            const int EDGE_INDICES[24] = int[24](
              0, 1,  1, 3,  3, 2,  2, 0,  // front
              4, 5,  5, 7,  7, 6,  6, 4,  // rear
              2, 6,  3, 7,  1, 5,  0, 4
            );
            
            void main() {
              int vertexIndex = EDGE_INDICES[gl_VertexID];
              gl_Position = Projection * ModelView * vec4(CUBE_VERTICES[vertexIndex], 1.0);
            }
            """,
            GL.GL_VERTEX_SHADER)
        fragment_shader = compileShader(
            """#version 430
            out vec4 FragColor;
            
            void main() {
              FragColor = vec4(1.0, 1.0, 1.0, 1.0);
            }
            """,
            GL.GL_FRAGMENT_SHADER)
        self.shader = compileProgram(vertex_shader, fragment_shader)
        
    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        GL.glUseProgram(self.shader)
        GL.glUniformMatrix4fv(0, 1, False, camera.projection)
        model_view = self.model_matrix @ camera.view_matrix
        GL.glUniformMatrix4fv(4, 1, False, model_view.pack())
        GL.glLineWidth(3)
        GL.glDrawArrays(GL.GL_LINES, 0, 24)
    
    def dispose_gl(self):
        GL.glDeleteProgram(self.shader)
        self.shader = 0
        super().dispose_gl()

    @property
    def model_center(self):
        return self._model_matrix.model_center

    @model_center.setter
    def model_center(self, center):
        self.model_matrix.model_center = center

    @property
    def scale(self):
        return self._model_matrix.scale

    @scale.setter
    def scale(self, scale):
        self.model_matrix.scale = scale
