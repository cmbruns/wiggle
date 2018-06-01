#version 430

const int STYLE_BASIC_POINT = 1;
const int STYLE_ADJUSTED_POINT = 2;
const int STYLE_HOVERED_POINT = 3;

layout(location = 0) in vec3 inPosition;
layout(location = 1) in int inStyle;

layout(location = 0) uniform mat4 projection = mat4(1);
layout(location = 4) uniform mat4 model_view = mat4(1);

out int style;

void main()
{
    vec4 rot_only = model_view * vec4(inPosition, 0.0);
    gl_Position = projection * vec4(rot_only.xyz, 1.0);
    style = inStyle;
}
