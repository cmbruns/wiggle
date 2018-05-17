#version 430

layout(location = 0) in vec3 inPosition;

layout(location = 0) uniform mat4 projection = mat4(1);
layout(location = 4) uniform mat4 model_view = mat4(1);

void main()
{
  gl_Position = projection * model_view * vec4(inPosition, 1.0);
}
