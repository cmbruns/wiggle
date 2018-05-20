#version 430

// synchronize these values with those in PlaneMaterial
const int RENDER_MODE_SOLID = 0;
const int RENDER_MODE_TEXTURE = 1;
const int RENDER_MODE_CHECKER = 2;
const int RENDER_MODE_TEX_COORD = 3;
uniform int render_mode = RENDER_MODE_SOLID;

uniform sampler2D image;
uniform vec3 plane_color = vec3(0.6, 0.6, 0.3);

in vec4 intersection_m;  // in model space
in vec4 intersection_w;  // in world space
in vec4 intersection_c;  // in clip space

out vec4 frag_color;

vec2 edge_distance(in vec2 tc)
{
    // todo: remove remaining moire pattern at middle distances
    vec2 ftc = fract(tc);
    vec2 edge_distance = min(ftc, vec2(1) - ftc);
    vec2 width = fwidth(tc); // todo: vary this method
    vec2 edge_dist_pixels = 2.0 * edge_distance/width; // todo: vary coefficient
    edge_dist_pixels = clamp(edge_dist_pixels, 0.0, 1.0);
    return edge_dist_pixels;
}

vec4 tc_color(in vec2 tc)
{
    return vec4(fract(tc), 0.6, 1);
}

vec4 tc_color_antialias(in vec2 tc)
{
    vec2 ftc = fract(tc);
    vec2 edge_dist_pixels = edge_distance(tc);
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

vec4 checker_color_antialias(in vec2 uv)
{
    vec4 c1 = vec4(0.1, 0.1, 0.1, 1);
    vec4 c2 = vec4(0.6, 0.6, 0.5, 1);
    vec4 edge_color = mix(c1, c2, 0.5);
    // http://developer.download.nvidia.com/books/HTML/gpugems/gpugems_ch25.html
    float p = mod(floor(uv.x) + floor(uv.y), 2);
    vec4 point_color = c2;
    if (p < 1) point_color = c1;
    vec2 ed = edge_distance(uv);
    float a = min(ed.x, ed.y);
    return mix(edge_color, point_color, a);
}

vec4 image_color(vec2 tc)
{
    return texture(image, tc);
}

vec4 solid_color(vec2 tc)
{
    return vec4(plane_color, 1);
}

vec4 texture_color(vec2 tc)
{
    // todo: consider other forms of shader composition
    switch (render_mode) {
        case RENDER_MODE_SOLID: return solid_color(tc);
        case RENDER_MODE_TEXTURE: return image_color(tc);
        case RENDER_MODE_CHECKER: return checker_color_antialias(tc);
        case RENDER_MODE_TEX_COORD: return tc_color_antialias(tc);
    }
    return checker_color_antialias(tc);
}

void main()
{
    gl_FragDepth = (intersection_c.z / intersection_c.w + 1.0) / 2.0;
    vec2 tc = intersection_m.xz / intersection_m.w;
    frag_color = texture_color(tc);
}
