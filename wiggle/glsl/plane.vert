#version 430

// Vertex shader for rendering an infinite plane.

// Standard 3D graphics homogeneous matrices
layout(location = 0) uniform mat4 projection = mat4(1);
layout(location = 1) uniform mat4 view = mat4(1);
// model matrix is used to transform plane from Y==0,up initial orientation
layout(location = 2) uniform mat4 model = mat4(1);

// Input screen-quad corners, in clip space.
// (the plane might fill the whole screen, if you look toward it)
in vec3 position_c;

// Output one custom clip plane, to discard everything above the plane horizon.
// Explicit declaration of built-in gl_ClipDistance with size 1.
out float gl_ClipDistance[1];

// Output homogeneous coordinates of view/plane intersection,
// in world space and clip space
out vec4 intersection_w;
out vec4 intersection_c;


// Extract camera location in world sapce, from view matrix
vec3 cam_pos_w_from_view(in mat4 view)
{
    // assuming no scaling
    mat3 rot = mat3(view);
    vec3 d = vec3(view[3]);
    return -d * rot;
}


void main()
{
    // Screen-quad corner coordinates arrive dirctly in clip-space
 	gl_Position = vec4(position_c, 1);

    // Initial plane model faces up at Y == 0
    const vec4 plane_m = vec4(0, 1, 0, 0);

    // Transform plane to world space
    vec4 plane_w = model * plane_m;

    // Compute screen-quad corner location in world space
    mat4 w_from_c = inverse(projection * view);
    vec4 position_w = w_from_c * vec4(position_c, 1);

    // Extract camera location in world space
    vec3 cam_pos_w = cam_pos_w_from_view(view);

    // View direction, not normalized
    vec3 view_dir_w = position_w.xyz/position_w.w - cam_pos_w;

    // Compute intersection of view ray with plane.
    // Homogenous coordinates allow correct shader interpolation.
    intersection_w = vec4(
        cross(plane_w.xyz, cross(cam_pos_w, view_dir_w)) - plane_w.w * view_dir_w,  // xyz
        dot(plane_w.xyz, view_dir_w));  // w

    // Clip away everything above the horizon.
    // (this also allows MSAA to function on the horizon, unlike discard)
    gl_ClipDistance[0] = -intersection_w.w;

    // Precompute intersection in clip coordinates, to simplify
    // gl_FragDepth computation
    intersection_c = projection * view * intersection_w;
}
