// Static CRT finish: vignette, faint scanlines, cheap glow on bright text.
// Never reads iTime, so it is safe with custom-shader-animation = false (renders only when the terminal updates).

const float GLOW = 0.30;           // strength of the glow added back onto bright pixels
const float GLOW_THRESHOLD = 0.35; // blurred brightness below this gets no glow, so the dark background stays untouched
const float GLOW_RADIUS = 1.5;     // tap offset in pixels
const float SCANLINE = 0.05;       // how much every third pixel row is darkened
const float VIGNETTE = 0.20;       // corner darkening

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy;
    vec4 base = texture(iChannel0, uv);

    // 4 diagonal taps -> small box blur
    vec2 px = GLOW_RADIUS / iResolution.xy;
    vec3 blur = 0.25 * (
        texture(iChannel0, uv + vec2( px.x,  px.y)).rgb +
        texture(iChannel0, uv + vec2(-px.x,  px.y)).rgb +
        texture(iChannel0, uv + vec2( px.x, -px.y)).rgb +
        texture(iChannel0, uv + vec2(-px.x, -px.y)).rgb);
    float bright = max(blur.r, max(blur.g, blur.b));
    vec3 rgb = base.rgb + blur * GLOW * smoothstep(GLOW_THRESHOLD, 1.0, bright);

    float scan = 1.0 - SCANLINE * step(mod(floor(fragCoord.y), 3.0), 0.5);
    float vig = 1.0 - VIGNETTE * smoothstep(0.35, 0.9, length(uv - 0.5));
    rgb *= scan * vig;

    // Ghostty composites premultiplied alpha, so colour must not exceed alpha
    fragColor = vec4(rgb, max(base.a, max(rgb.r, max(rgb.g, rgb.b))));
}
