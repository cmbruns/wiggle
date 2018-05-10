#version 430

layout(location = 0) uniform mat4 Projection = mat4(1);
layout(location = 4) uniform mat4 ModelView = mat4(1);

const vec3 VERTEXES[8] = vec3[8](
  vec3(-0.5, -0.5, -0.5),
  vec3(0.5, -0.5, -0.5),
  vec3(-0.5, 0.5, -0.5),
  vec3(0.5, 0.5, -0.5),
  vec3(-0.5, -0.5, 0.5),
  vec3(0.5, -0.5, 0.5),
  vec3(-0.5, 0.5, 0.5),
  vec3(0.5, 0.5, 0.5)
);

const int EDGE_INDEXES[24] = int[24](
  0, 1,
  0, 2,
  0, 4,
  1, 3,
  1, 5,
  2, 3,
  2, 6,
  3, 7,
  4, 5,
  4, 6,
  5, 7,
  6, 7
);

void main()
{
  int vertexIndex = EDGE_INDEXES[gl_VertexID];
  vec3 position = VERTEXES[vertexIndex];
  gl_Position = Projection * ModelView * vec4(position, 1.0);
}
