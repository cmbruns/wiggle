#version 430

layout(location = 0) in vec3 inPosition;

layout(location = 0) uniform mat4 projection = mat4(1);
layout(location = 4) uniform mat4 model_view = mat4(1);

void main()
{
    vec4 rot_only = model_view * vec4(inPosition, 0.0);
    gl_Position = projection * vec4(rot_only.xyz, 1.0);
}
