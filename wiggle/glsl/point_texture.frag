#version 430

const int STYLE_BASIC_POINT = 1;
const int STYLE_ADJUSTED_POINT = 2;
const int STYLE_HOVERED_POINT = 3;

flat in int frag_style;

uniform sampler2D image;

out vec4 frag_color;

void main() {
    vec4 color4 = vec4(0.5, 0.5, 0.5, 0.4);
    if (STYLE_HOVERED_POINT == frag_style)
        color4 = vec4(1.0, 1.0, 0.3, 0.7);
    else if (STYLE_ADJUSTED_POINT == frag_style)
        color4 = vec4(0.8, 0.8, 0.8, 0.6);
    vec4 texColor = texture(image, gl_PointCoord.st);
	frag_color = texColor * color4;
	gl_FragDepth = 1.0;
}
