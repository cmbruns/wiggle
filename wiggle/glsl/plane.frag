#version 430

in vec4 intersection_c;  // in clip space
in vec4 intersection_w;  // in world space

out vec4 frag_color;

void main() {
    gl_FragDepth = (intersection_c.z / intersection_c.w + 1.0) / 2.0;

    // todo: this only works for a ground plane
    vec2 tex_coord = intersection_w.xz / intersection_w.w;

    vec2 edge_dist_tc = vec2(0.5) - abs(fract(tex_coord) - vec2(0.5));
    vec2 edge_dist_pixel = edge_dist_tc = fwidth(tex_coord);

    vec2 edge_nearness = 2.0 * abs(fract(tex_coord) - vec2(0.5));
    vec2 edge_distance = vec2(1) - edge_nearness;
    vec2 edge_dist_pixels = clamp(edge_distance/fwidth(tex_coord), 0, 1);
    vec2 color1 = mix(vec2(0.5, 0.5), fract(tex_coord), edge_dist_pixels);
    frag_color = vec4(color1, 0.5, 1);
    // frag_color = vec4(edge_distance, 0.5, 1);
    return;

    vec2 color = fract(tex_coord);
    float red = smoothstep(color.r, 0.5, edge_dist_pixel.x);
    float green = smoothstep(color.g, 0.5, edge_dist_pixel.y);

    // far away antialiasing
    // todo:

    frag_color = vec4(red, green, 0.5, 1);
    // frag_color = vec4(0.5, 0.8, 0.5, 1.0);

}
