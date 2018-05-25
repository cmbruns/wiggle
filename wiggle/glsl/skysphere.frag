#version 430

uniform sampler2D image;
layout(location = 0) uniform mat4 projection = mat4(1);
layout(location = 2) uniform mat4 view = mat4(1);

in vec4 position_w;
in vec3 cam_pos_w;

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
    vec3 p_w = position_w.xyz / position_w.w;
    vec3 view_dir_w = p_w - cam_pos_w;

    vec3 sphere_center_w = vec3(0, 1.7, 0);
    float sphere_radius_w = 2.0;

    vec3 x0 = cam_pos_w - sphere_center_w;
    vec3 x1 = normalize(view_dir_w);
    float qa = 1.0;
    float qb = 2.0 * dot(x0, x1);
    float qc = dot(x0, x0) - sphere_radius_w * sphere_radius_w;
    float determinant = qb * qb - 4.0 * qa * qc;
    if (determinant <= 0)
        discard;
    float t_back = (-qb + sqrt(determinant))/(2.0 * qa);
    vec3 p_back_w = sphere_center_w + x0 + t_back * x1;
    vec3 direction = normalize(p_back_w - sphere_center_w);
    vec4 p_back_c = projection * view * vec4(p_back_w, 1);
    gl_FragDepth = (p_back_c.z / p_back_c.w + 1) / 2.0;
    if (gl_FragDepth < 0)
        discard;

    frag_color = equirect_color(direction, image);
    // frag_color = vec4(0.5 * (direction + vec3(1)), 1);
}
