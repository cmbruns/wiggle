#version 430 core

/*
  Geometry shader
  Computes normal vector per-triangle.

  Requires that vertices passed from vertex shader are in view space.

  Also projects the vertices and rejects back faces.
*/

layout(location = 0) uniform mat4 Projection = mat4(1);
layout(location = 4) uniform mat4 ModelView = mat4(1);

layout (triangles) in ;
layout (triangle_strip) out;
layout (max_vertices = 3) out;

out vec3 normal;

vec4 view(int i) {
    return ModelView * gl_in[i].gl_Position;
}

/*
          b---a
           \ /
            c
*/

bool compute_normal(vec4 triangle[3])
{
    a = triangle[0].xyz / triangle[0].w;
    b = triangle[1].xyz / triangle[1].w;
    c = triangle[2].xyz / triangle[2].w;
    vec3 n1 = cross(b - a, c - a);
    if (n1.z <= 0)
        return false; // back facing
    normal = normalize(n1);
    return true;
}

void emit(vec4 triangle[3])
{
    for (int i = 0; i < 3; ++i)
    {
        gl_Position = Projection * triangle[i];
        EmitVertex();
    }
    EndPrimitive();
}

void main(void)
{
    vec4 triangle[3] = vec4[3](view(0), view(1), view(2));
    if (compute_normal(triangle))
        emit(triangle);
}
