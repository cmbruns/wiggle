#version 430

layout(location = 0) in vec3 inPosition;

layout(location = 0) uniform mat4 Projection = mat4(1);
layout(location = 4) uniform mat4 ModelView = mat4(1);

void main()
{
  gl_Position = Projection * ModelView * vec4(inPosition, 1.0);
}
