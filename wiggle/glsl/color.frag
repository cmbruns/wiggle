#version 430

uniform vec3 color = vec3(0.5);

out vec4 frag_color;

void main() {
  frag_color = vec4(color, 1.0);
}
