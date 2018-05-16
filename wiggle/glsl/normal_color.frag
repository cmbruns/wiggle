#version 430

in vec3 vNormal_w;
out vec4 FragColor;

void main() {
  vec3 color = 0.5 * (vNormal_w + vec3(1));
  FragColor = vec4(color, 1.0);
}
