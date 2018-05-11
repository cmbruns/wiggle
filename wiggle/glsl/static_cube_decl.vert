// static vertex data for a cube

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
