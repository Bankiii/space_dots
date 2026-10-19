#version 300 es
precision highp float;
in vec2 v_texcoord;
uniform sampler2D tex;
layout(location = 0) out vec4 fragColor;

void main() {
    vec2 uv = v_texcoord;

    // aberración cromática muy leve
    float off = 0.0007;
    float r = texture(tex, uv + vec2(off, 0.0)).r;
    float g = texture(tex, uv).g;
    float b = texture(tex, uv - vec2(off, 0.0)).b;
    vec3 c = vec3(r, g, b);

    // tinte ámbar
    c *= vec3(1.05, 0.95, 0.78);

    // scanlines: una de cada tres filas un poco más oscura
    c *= 1.0 - 0.10 * step(2.0, mod(gl_FragCoord.y, 3.0));

    // viñeta en las esquinas
    float d = distance(uv, vec2(0.5));
    c *= 1.0 - 0.35 * smoothstep(0.35, 0.85, d);

    fragColor = vec4(c, 1.0);
}
