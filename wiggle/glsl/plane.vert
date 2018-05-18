#version 430

in vec3 position_c;
out vec4 intersection_w;
out vec4 intersection_c;

layout(location = 0) uniform mat4 projection = mat4(1);
layout(location = 4) uniform mat4 model_view = mat4(1);
uniform vec4 plane_equation_w = vec4(0, 1, 0, 0); // up-facing ground plane at Y == 0


vec3 cam_pos_w_from_model_view(in mat4 model_view)
{
    // assuming no scaling
    mat3 rot = mat3(model_view);
    vec3 d = vec3(model_view[3]);
    return -d * rot;
}


void main() {
	gl_Position = vec4(position_c, 1);

    mat4 world_from_clip = inverse(projection * model_view);
    vec4 position_w = world_from_clip * vec4(position_c, 1);
    vec3 cam_pos_w = cam_pos_w_from_model_view(model_view);
    vec3 view_dir_w = position_w.xyz/position_w.w - cam_pos_w;
    intersection_w = vec4(
        cross(plane_equation_w.xyz, cross(cam_pos_w, view_dir_w)) - plane_equation_w.w * view_dir_w,  // xyz
        dot(plane_equation_w.xyz, view_dir_w));  // w

    gl_ClipDistance[0] = -intersection_w.w;

    intersection_c = projection * model_view * intersection_w;
}
