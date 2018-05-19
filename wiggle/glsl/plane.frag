#version 430

in vec4 intersection_c;  // in clip space
in vec4 intersection_w;  // in world space

out vec4 frag_color;

vec4 tc_color(in vec2 tc)
{
    return vec4(fract(tc), 0.6, 1);
}

vec4 tc_color_antialias(in vec2 tc)
{
    // todo: remove remaining moire pattern at middle distances
    vec2 ftc = fract(tc);
    vec2 edge_distance = min(ftc, vec2(1) - ftc);
    vec2 width = fwidth(tc); // todo: vary this method
    vec2 edge_dist_pixels = 0.7 * edge_distance/width; // todo: vary coefficient
    edge_dist_pixels = clamp(edge_dist_pixels, 0.0, 1.0);
    vec2 color1 = mix(vec2(0.5, 0.5), ftc, edge_dist_pixels);
    return vec4(color1, 0.6, 1);
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

vec4 texture_color(vec2 tc)
{
    return tc_color_antialias(tc);
}

void main()
{
    gl_FragDepth = (intersection_c.z / intersection_c.w + 1.0) / 2.0;

    // todo: this texture coordinate only works for a ground plane
    vec2 tc = intersection_w.xz / intersection_w.w;

    frag_color = texture_color(tc);
}
