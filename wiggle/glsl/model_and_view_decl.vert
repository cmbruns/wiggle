layout(location = 0) uniform mat4 Projection = mat4(1);
layout(location = 4) uniform mat4 ModelView = mat4(1);

void transform(in vec3 position)
{
    gl_Position = Projection * ModelView * vec4(position, 1.0);
}