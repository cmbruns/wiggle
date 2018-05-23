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

vec4 equirect_color(vec3 dir, sampler2D image)
{
    const float PI = 3.1415926535897932384626433832795;
    float longitude = 0.5 * atan(dir.x, -dir.z) / PI + 0.5; // range [0-1]
    float r = length(dir.xz);
    float latitude = atan(dir.y, r) / PI + 0.5; // range [0-1]
    vec2 tex_coord = vec2(longitude, latitude);

    // Use explicit gradients, to preserve anisotropic filtering during mipmap lookup
    vec2 dpdx = dFdx(tex_coord);
    if (dpdx.x > 0.5) dpdx.x -= 1; // use "repeat" wrapping on gradient
    if (dpdx.x < -0.5) dpdx.x += 1;
    vec2 dpdy = dFdy(tex_coord);
    if (dpdy.x > 0.5) dpdy.x -= 1; // use "repeat" wrapping on gradient
    if (dpdy.x < -0.5) dpdy.x += 1;

    return textureGrad(image, tex_coord, dpdx, dpdy);
}

void main()
{
    vec4 view_direction = homog_subtract(position_w, cam_pos_w);
    frag_color = equirect_color(normalize(view_direction.xyz), image);
    // frag_color = vec4(0.5 * (normalize(view_direction.xyz) + vec3(1)), 1);
}
