#version 430

// Standard 3D graphics homogeneous matrices
layout(location = 0) uniform mat4 projection = mat4(1);
// model matrix is used to transform viewpoint from (0,0,0) to actual viewpoint location
layout(location = 1) uniform mat4 model = mat4(1);
layout(location = 2) uniform mat4 view = mat4(1);

// Input screen-quad corners, in clip space.
// (the sky might fill the whole screen)
in vec3 position_c;

out vec4 position_w;
out vec4 cam_pos_w;

void main() {
    position_w = inverse(projection * view) * vec4(position_c, 1);
    cam_pos_w = inverse(view) * vec4(0, 0, 0, 1);
	gl_Position = vec4(position_c, 1.0);
}
