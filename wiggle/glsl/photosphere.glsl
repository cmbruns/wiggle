
vec4 equirect_color(vec3 dir, sampler2D image)
{
    const float PI = 3.1415926535897932384626433832795;
    float longitude = 0.5 * atan(dir.x, -dir.z) / PI + 0.5; // range [0-1]
    float r = length(dir.xz);
    float latitude = atan(dir.y, r) / PI + 0.5; // range [0-1]
    vec2 tex_coord = vec2(longitude, latitude);

    // Use explicit gradients, to preserve anisotropic filtering during mipmap lookup
    vec2 dpdx = dFdx(tex_coord);
    vec2 dpdy = dFdy(tex_coord);
    if (true) {
        if (dpdx.x > 0.5) dpdx.x -= 1; // use "repeat" wrapping on gradient
        if (dpdx.x < -0.5) dpdx.x += 1;
        if (dpdy.x > 0.5) dpdy.x -= 1; // use "repeat" wrapping on gradient
        if (dpdy.x < -0.5) dpdy.x += 1;
    }

    return textureGrad(image, tex_coord, dpdx, dpdy);
}
