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

out vec3 vNormal_v;

vec4 view(int i) {
    return ModelView * gl_in[i].gl_Position;
}

/*
          b---a
           \ /
            c
*/

bool compute_normal(vec4 vTriangle_v[3])
{
    vec3 vA_v = vTriangle_v[0].xyz / vTriangle_v[0].w;
    vec3 vB_v = vTriangle_v[1].xyz / vTriangle_v[1].w;
    vec3 vC_v = vTriangle_v[2].xyz / vTriangle_v[2].w;
    vec3 vN_v = cross(vB_v - vA_v, vC_v - vA_v);
    if (dot(vN_v, vA_v) >= 0)
        return false; // back facing
    vNormal_v = normalize(vN_v);
    return true;
}

void emit(vec4 vTriangle_v[3])
{
    for (int i = 0; i < 3; ++i)
    {
        gl_Position = Projection * vTriangle_v[i];
        EmitVertex();
    }
    EndPrimitive();
}

void main(void)
{
    vec4 vTriangle_v[3] = vec4[3](view(0), view(1), view(2));
    if (compute_normal(vTriangle_v))
        emit(vTriangle_v);
}
