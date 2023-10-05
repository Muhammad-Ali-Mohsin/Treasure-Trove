#version 330 core

uniform int screen;  // The input screen
uniform sampler2D screen_texture;  // The input texture
uniform sampler2D ldisplay_texture;  // The texture for the ui such as the compass
uniform sampler2D noise_texture; // The noise texture used for the shadowy border
uniform sampler2D light_map;    // The light map texture
uniform float time;
uniform vec3 daylight;   // Time of day (0.0 to 1.0)

in vec2 uv;
out vec4 f_color;

void main()
{
    // Gets the initial color from the texture
    vec4 screen_color = texture(screen_texture, uv);
    
    if (screen == 0) {
        // Gets the color as a result of multiplying the initial color by the daytime
        vec3 daylight_color = screen_color.rgb * daylight;  

        // Multiplies the change in color by the value in the light map to create the light
        vec3 light_color = texture(light_map, uv).rgb * (screen_color.rgb - daylight_color);
        
        f_color = vec4(screen_color.rgb * daylight + light_color, screen_color.a);

        vec2 px_uv = vec2(floor(uv.x * 1920) / 1920, floor(uv.y * 1080) / 1080);
        vec2 px_uv2 = vec2(floor(uv.x * 1920) / 1920, floor(uv.y * 1080) / 1080);

        float intensity = (1 - (daylight.r + daylight.g + daylight.b) / 3) * 0.5;
        float center_dis = distance(px_uv, vec2(0.5, 0.5));
        float noise_val = center_dis + texture(noise_texture, vec2(px_uv2.x * 1.52 * 2 + time * 0.05, px_uv2.y * 2 - time * 0.1)).r * intensity;
        vec4 dark = vec4(0.0, 0.0, 0.0, 1.0);
        float darkness = max(0, noise_val - 0.7) * 10;
        float vignette = max(0, center_dis * center_dis - 0.1) * 7 * intensity;
        darkness += vignette;
        f_color = (1 - darkness) * f_color;

        // Output the result
        vec4 ldisplay_color = texture(ldisplay_texture, uv);
        if (ldisplay_color.a > 0) {
            f_color = ldisplay_color;
        }

    }
    else {
        f_color = screen_color;
    }
}
