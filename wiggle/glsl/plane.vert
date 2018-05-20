#version 430

// Vertex shader for rendering an infinite plane.

// Standard 3D graphics homogeneous matrices
layout(location = 0) uniform mat4 projection = mat4(1);
// model matrix is used to transform plane from Y==0,up initial orientation
layout(location = 4) uniform mat4 model_view = mat4(1);

// Input screen-quad corners, in clip space.
// (the plane might fill the whole screen, if you look toward it)
in vec3 position_c;

// Output one custom clip plane, to discard everything above the plane horizon.
// Explicit declaration of built-in gl_ClipDistance with size 1.
out float gl_ClipDistance[1];

// Output homogeneous coordinates of view/plane intersection,
// in model space and clip space
out vec4 intersection_m; // for computing texture coordinate
out vec4 intersection_w; // for computing parallax offset
out vec4 intersection_c; // for computing gl_FragDepth


vec3 dehomog(vec4 v)
{
    return v.xyz/v.w;
}


void main()
{
    // Screen-quad corner coordinates arrive dirctly in clip-space.
    // Pass them through unchanged.
 	gl_Position = vec4(position_c, 1);

    // Initial plane model faces up at Y == 0
    const vec4 plane_m = vec4(0, 1, 0, 0);

    // Compute the view/plane intersection in model space,
    // to enable sensible computation of texture coordinates.

    // Compute camera location in model space
    const vec4 cam_pos_v = vec4(0, 0, 0, 1);
    mat4 m_from_v = inverse(model_view);
    vec3 cam_pos_m = dehomog(m_from_v * cam_pos_v);

    // Compute screen-quad corner location in model space
    mat4 v_from_c = inverse(projection);
    vec3 corner_m = dehomog(m_from_v * v_from_c * vec4(position_c, 1));

    // View direction (not normalized, normalization not required)
    vec3 view_dir_m = corner_m - cam_pos_m;

    // Compute intersection of view ray with plane, in model space.
    // Homogenous coordinates allow correct shader interpolation.
    // I expect the compiler to apply the obvious simplifications, since
    // plane_m is const. I'm leaving the full equation here, because it took
    // a while to derive.
    intersection_m = vec4(
        cross(plane_m.xyz, cross(cam_pos_m, view_dir_m)) - plane_m.w * view_dir_m,  // xyz
        dot(plane_m.xyz, view_dir_m));  // w

    // Clip away everything above the horizon.
    // (this also allows MSAA to function on the horizon, unlike discard)
    gl_ClipDistance[0] = -intersection_m.w;

    // World coordinates too, for parallax adjustment
    intersection_w = model_view * intersection_m;

    // Precompute intersection in clip coordinates, to simplify
    // gl_FragDepth computation
    intersection_c = projection * intersection_w;
}
