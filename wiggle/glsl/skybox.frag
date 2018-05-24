#version 430

uniform sampler2D image;

in vec4 position_w;
in vec4 cam_pos_w;

out vec4 frag_color;

vec4 homog_subtract(vec4 a, vec4 b)
{
    float out_w = a.w;
    if (abs(b.w) < abs(a.w))
        return a * b.w/a.w - b;
    else
        return a - b * a.w/b.w;
}

#pragma include "wiggle/glsl/photosphere.glsl"

void main()
{
    vec4 view_direction = homog_subtract(position_w, cam_pos_w);
    frag_color = equirect_color(normalize(view_direction.xyz), image);
}
