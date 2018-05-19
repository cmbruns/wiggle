#version 430

in vec4 intersection_c;  // in clip space
in vec4 intersection_w;  // in world space

out vec4 frag_color;

vec4 tc_color(in vec2 uv)
{
    return vec4(fract(uv), 1, 1);
}

vec4 checker_color(in vec2 uv)
{
    vec4 c1 = vec4(0.1, 0.1, 0.1, 1);
    vec4 c2 = vec4(0.6, 0.6, 0.5, 1);
    // http://developer.download.nvidia.com/books/HTML/gpugems/gpugems_ch25.html
    float p = mod(floor(uv.x) + floor(uv.y), 2);
    if (p < 1) return c1;
    return c2;
}

vec4 color(in vec2 uv)
{
    return checker_color(uv);
}

vec4 antialias(in vec2 uv)
{
    // http://developer.download.nvidia.com/books/HTML/gpugems/gpugems_ch25.html
    vec2 width = fwidth(uv);
    vec2 p0 = uv - 0.5 * width;
    vec2 p1 = uv + 0.5 * width;
    vec2 p2 = vec2(p0.x, p1.y);
    vec2 p3 = vec2(p1.x, p0.y);
    return 0.25 * (color(p0) + color(p1) + color(p2) + color(p3));
}

void main() {
    gl_FragDepth = (intersection_c.z / intersection_c.w + 1.0) / 2.0;

    // todo: this only works for a ground plane
    vec2 tex_coord = intersection_w.xz / intersection_w.w;

    // point_color and edge_color are texcoord texture specific
    vec4 point_color = vec4(fract(tex_coord), 1, 1);
    vec4 edge_color = vec4(0.5, 0.5, 1, 1); // wrong

    vec2 edge_nearness = 2.0 * abs(fract(tex_coord) - vec2(0.5));
    vec2 edge_distance = vec2(1) - edge_nearness;
    vec2 edge_dist_pixels = 0.4 * edge_distance/fwidth(tex_coord);
    edge_dist_pixels = clamp(edge_dist_pixels, 0, 1);
    vec2 blend = edge_dist_pixels;
    vec2 color1 = mix(vec2(0.5, 0.5), fract(tex_coord), blend);
    frag_color = vec4(color1, 0.5, 1);
    return;
}
