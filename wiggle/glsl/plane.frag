#version 430

in vec4 intersection_c;  // in clip space
in vec4 intersection_w;  // in world space

out vec4 frag_color;

vec4 tc_color(in vec2 tc)
{
    // compute color on other side of edge
    vec2 ftc = fract(tc);
    vec2 edge_distance = min(ftc, vec2(1) - ftc);
    vec2 edge_mask = vec2(0, 1);
    if (edge_distance.x < edge_distance.y) edge_mask = vec2(1, 0);

    // point_color and edge_color are texcoord texture specific
    vec4 point_color = vec4(ftc, 1, 1);

    // todo: texture coordinate across the edge

    vec2 width = fwidth(tc); // todo: vary this method
    vec4 edge_color = vec4(0.5, point_color.gba);
    if (width.x < width.y) edge_color = vec4(point_color.r, 0.5, point_color.ba);

    vec2 edge_dist_pixels = edge_distance/width;
    edge_dist_pixels = clamp(edge_dist_pixels, 0.0, 1.0);
    vec2 blend = edge_dist_pixels;
    vec2 color1 = mix(vec2(0.5, 0.5), ftc, blend);
    return vec4(color1, 1, 1);
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

void main() {
    gl_FragDepth = (intersection_c.z / intersection_c.w + 1.0) / 2.0;

    // todo: this tex_coord only works for a ground plane
    vec2 tc = intersection_w.xz / intersection_w.w;

    frag_color = tc_color(tc);
}
