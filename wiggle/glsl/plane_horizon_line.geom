#version 430 core

/*
  Geometry shader
  Emits horizon line for infinite plane.
*/

layout (triangles) in ;
layout (line_strip, max_vertices = 2) out;

// Pass dummy versions of vertex shader outputs; they won't be used in
// wireframe mode.
out vec4 intersection_m;
out vec4 intersection_w;
out vec4 intersection_c;

int check_segment(in int ix1, in int ix2)
{
    float c1 = gl_in[ix1].gl_ClipDistance[0];
    float c2 = gl_in[ix2].gl_ClipDistance[0];

    if (c1 * c2 > 0) return 0; // segment does not intersect horizon

    float alpha = c1 / (c1 - c2);
    gl_Position = mix(gl_in[ix1].gl_Position, gl_in[ix2].gl_Position, alpha);
    gl_Position.z = gl_Position.w;  // push depth to 1

    EmitVertex();
    return 1;
}

void main(void)
{
    // Pass dummy versions of vertex shader outputs; they won't be used in
    // wireframe mode.
    intersection_c = vec4(1);
    intersection_w = vec4(1);
    intersection_m = vec4(1);

    int point_count = 0;
    point_count += check_segment(0, 1);
    point_count += check_segment(1, 2);
    point_count += check_segment(2, 0);
    if (point_count > 0) EndPrimitive();
}
