# file color_cube_actor.py

"""
Color cube for use in "hello world" 3D apps
"""

from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram

from .renderer import AutoInitRenderer
from .matrix import ModelMatrix


class ColorCubeActor(AutoInitRenderer):
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
            layout(location = 8) uniform float Size = 0.3;
            
            const vec3 UNIT_CUBE[8] = vec3[8](
              vec3(-1.0, -1.0, -1.0), // 0: lower left rear
              vec3(+1.0, -1.0, -1.0), // 1: lower right rear
              vec3(-1.0, +1.0, -1.0), // 2: upper left rear
              vec3(+1.0, +1.0, -1.0), // 3: upper right rear
              vec3(-1.0, -1.0, +1.0), // 4: lower left front
              vec3(+1.0, -1.0, +1.0), // 5: lower right front
              vec3(-1.0, +1.0, +1.0), // 6: upper left front
              vec3(+1.0, +1.0, +1.0)  // 7: upper right front
            );
            
            const vec3 UNIT_CUBE_NORMALS[6] = vec3[6](
              vec3(0.0, 0.0, -1.0),
              vec3(0.0, 0.0, 1.0),
              vec3(1.0, 0.0, 0.0),
              vec3(-1.0, 0.0, 0.0),
              vec3(0.0, 1.0, 0.0),
              vec3(0.0, -1.0, 0.0)
            );
            
            const int CUBE_INDICES[36] = int[36](
              0, 1, 2, 2, 1, 3, // front
              4, 6, 5, 6, 5, 7, // back
              0, 2, 4, 4, 2, 6, // left
              1, 3, 5, 5, 3, 7, // right
              2, 6, 3, 6, 3, 7, // top
              0, 1, 4, 4, 1, 5  // bottom
            );
            
            out vec3 _color;
            
            void main() {
              _color = vec3(1.0, 0.0, 0.0);
              int vertexIndex = CUBE_INDICES[gl_VertexID];
              int normalIndex = gl_VertexID / 6;
              
              _color = UNIT_CUBE_NORMALS[normalIndex];
              if (any(lessThan(_color, vec3(0.0)))) {
                  _color = vec3(1.0) + _color;
              }
            
              gl_Position = Projection * ModelView * vec4(UNIT_CUBE[vertexIndex] * Size, 1.0);
            }
            """,
            GL.GL_VERTEX_SHADER)
        fragment_shader = compileShader(
            """#version 430
            in vec3 _color;
            out vec4 FragColor;
            
            void main() {
              FragColor = vec4(_color, 1.0);
            }
            """,
            GL.GL_FRAGMENT_SHADER)
        self.shader = compileProgram(vertex_shader, fragment_shader)
        
    def display_gl(self, camera, *args, **kwargs):
        super().display_gl(camera, *args, **kwargs)
        GL.glUseProgram(self.shader)
        GL.glUniformMatrix4fv(0, 1, False, camera.projection)
        GL.glUniformMatrix4fv(4, 1, False, camera.view_matrix)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 36)
    
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
