# file color_cube_actor.py

"""
Color cube for use in "hello world" 3D apps
"""

from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram

from wiggle.actor.base_actor import BaseActor


class ColorCubeActor(BaseActor):
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
            
            const vec3 UNIT_CUBE_NORMALS[6] = vec3[6](
              vec3( 0.0,  0.0, -1.0),
              vec3( 0.0,  0.0,  1.0),
              vec3(-1.0,  0.0,  0.0),
              vec3( 1.0,  0.0,  0.0),
              vec3( 0.0,  1.0,  0.0),
              vec3( 0.0, -1.0,  0.0)
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
            
              gl_Position = Projection * ModelView * vec4(CUBE_VERTICES[vertexIndex], 1.0);
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
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 36)
