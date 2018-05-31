#version 430

uniform sampler2D image;
uniform vec3 color = vec3(1);

out vec4 frag_color;

void main() {
    vec4 texColor = texture(image, gl_PointCoord.st);
	frag_color = vec4(texColor.rgb * color, 0.5 * texColor.a);
	gl_FragDepth = 1.0;
}
