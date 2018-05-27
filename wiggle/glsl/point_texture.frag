#version 430

uniform sampler2D image;

out vec4 frag_color;

void main() {
    vec4 texColor = texture(image, gl_PointCoord.st);
	frag_color = vec4(texColor.rgb, 0.5 * texColor.a);
}
