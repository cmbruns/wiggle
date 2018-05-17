#version 430 core

/*
  Geometry shader
  Computes normal vector per-triangle.

  Requires that vertices passed from vertex shader are in view space.

  Also projects the vertices and rejects back faces.
*/

layout(location = 0) uniform mat4 projection = mat4(1);
layout(location = 1) uniform mat4 model = mat4(1);
layout(location = 2) uniform mat4 view = mat4(1);

layout (triangles) in ;
layout (triangle_strip) out;
layout (max_vertices = 3) out;

out vec3 vNormal_w;

vec4 world(in int i) {
    return model * gl_in[i].gl_Position;
}

/*
          b---a
           \ /
            c
*/

bool compute_normal(in vec4 vTriangle_w[3])
{
    vec3 vA_w = vTriangle_w[0].xyz / vTriangle_w[0].w;
    vec3 vB_w = vTriangle_w[1].xyz / vTriangle_w[1].w;
    vec3 vC_w = vTriangle_w[2].xyz / vTriangle_w[2].w;
    vec3 vN_w = cross(vB_w - vA_w, vC_w - vA_w);
    vec4 vN_v = view * vec4(vN_w, 0);
    vec4 vA_v = view * vec4(vA_w, 1);
    if (dot(vN_v.xyz, vA_v.xyz) >= 0)
        return false; // back facing
    vNormal_w = normalize(vN_w);
    return true;
}

void emit(in vec4 vTriangle_w[3])
{
    for (int i = 0; i < 3; ++i)
    {
        gl_Position = projection * view * vTriangle_w[i];
        EmitVertex();
    }
    EndPrimitive();
}

void main(void)
{
    vec4 vTriangle_w[3] = vec4[3](world(0), world(1), world(2));
    if (compute_normal(vTriangle_w))
        emit(vTriangle_w);
}
