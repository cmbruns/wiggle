#version 430

/*
  Vertex shader.
  Does not even project or transform the input vertex.
  Intended for use with per_face_normals geometry shader.
 */

in vec3 position_in_world;

void main() {
	gl_Position = vec4(position_in_world, 1);
}
