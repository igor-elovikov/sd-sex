Degrees to Radians|`deg_to_rad(deg)`
asin|`asin(x)`
acos|`acos(x)`
Even Count|`evencount(Input)`
oddcount|`oddcount(Input)`
paritytest|`paritytest(Input)`
Ln|`ln(a)`
Pi|`pi()`
2 Pi|`_2pi()`
Pow|`pow(x, n)`
Roughness|`roughness(Roughness, CurrentLevel, TotalLevel, GlobalOpacity)`
Equality (float2)|`equality_float2(A, B)`
Equality (float3)|`equality_float3(A, B)`
Equality (boolean)|`equality_boolean(A, B)`
Equality (float4)|`equality_float4(A, B)`
Not Equal (float2)|`notequal_float2(A, B)`
Not Equal (float3)|`notequal_float3(A, B)`
Not Equal (float4)|`notequal_float4(A, B)`
Not Equal (boolean)|`notequal_boolean(A, B)`
Curve|`curve_function(curve, input)`
Merge (float4)|`merge_float4(x, y, z, w)`
Merge (float3)|`merge_float3(x, y, z)`
Distance (float3)|`distance_vec3(a, b)`
Distance (float2)|`distance_vec2(a, b)`
Length (float2)|`length_vec2(v)`
Length (float3)|`length_vec3(v)`
Sign|`sign(x)`
Reflect|`reflect(i, n)`
One minus|`oneminus(x)`
Fmod|`fmod(a, b)`
Frac|`frac(input)`
Cross product|`cross_product(a, b)`
Step|`step(a, x)`
Scalar division (float4)|`divide_float4(input, scalar)`
Scalar division (float3)|`divide_float3(input, scalar)`
Scalar division (float2)|`divide_float2(input, scalar)`
Clamp|`clamp(input, min, max)`
Normalize Vec2|`normalize_vec2(input)`
Normalize Vec3|`normalize_vec3(input)`
Normalize Vec4|`normalize_vec4(input)`
Smoothstep|`smoothstep(a, b, x)`
Saturate float2|`saturate_float2(input)`
Saturate|`saturate(input)`
Random Uniform [A, B[|`uniform_ab(A, B)`
Random Discrete [A, B]|`discrete_ab(A, B, Probability)`
Random Uniform [-1, 1[|`uniform_11()`
Random Uniform Float2 [A,B[|`uniform_f2_ab(A2, B2)`
Random Uniform Float3 [A,B[|`uniform_f3_ab(A, B)`
Random Uniform Float4 [A, B[|`uniform_f4_ab(A, B)`
Degrees to Turns|`degrees_to_turn(input)`
Global Random|`globalrandom(Input, Seed)`
Normal Distribution|`normal_distribution(radius, uniform_random)`
Directional Offset|`directional_offset(Direction, Distance)`
Matrix Multiply|`matrixmultiply(MatrixA, MatrixB)`
Rotation Matrix|`rotationmatrix(RotationW)`
Scale Matrix|`scalematrix(ScaleUV)`
Tile Matrix|`tilematrix(tiles_xy)`
Rotate Vec2|`rotate_vec2(vec2, angle, pivot)`
Wave|`wave(Amplitude, Frequency, greaterThanZero)`
[-1, 1] to [0,1]|`_1_1_to_0_1(Input)`
[0, 1] to [-1, 1]|`_0_1_to_1_1(Input)`
[0, 1] to [1, 0]|`_0_1_to_1_0(Input)`
Negate Float1|`negatefloat(Input)`
Height Balance|`height_balance_fn(Depth_Balance)`
Boolean to Float1|`booleantofloat1(Boolean)`
Turns to Degrees|`turnstodegrees(turns)`
Direction To Normal|`directiontonormal(Direction, slopeAngle, yUp)`
RGB to HSL|`rgbtohsl(RGB)`
HSL to RGB|`hsltorgb(HSL)`
Random Color|`random_color(RGB, RGB_Randomness)`
Random Luminosity|`random_luminosity(RGB, Luminosity_Randomness)`
RGB to HSV|`rgbtohsv(rgb)`
RGB to HSI|`rgbtohsi(rgb)`
RGB to HCL|`rgbtohcl(rgb)`
RGB Lightness Average|`rgb_lightness_average(rgb)`
RGB Lightness Hexcone|`rgb_lightness_hexcone(rgb)`
RGB Lightness Bi-Hexcone|`rgb_lightness_bihexcone(rgb)`
RGB Lightness Luma Rec. 601|`rgb_lightness_luma_rec601(rgb)`
RGB Lightness Luma Rec. 709|`rgb_lightness_luma_rec709(rgb)`
RGB Chroma Hexagonal|`rgb_chroma_hexagonal(rgb)`
RGB Chroma 2 Polar|`rgb_chroma_2_polar(rgb)`
RGB Hue Hexagonal|`rgb_hue_hexagonal(rgb)`
RGB Hue 2 Polar|`rgb_hue_2_polar(rgb)`
RGB Saturation HSV|`rgb_saturation_hsv(rgb)`
RGB Saturation HSL|`rgb_saturation_hsl(rgb)`
RGB Saturation HSI|`rgb_saturation_hsi(rgb)`
HSI to RGB|`hsitorgb(hsi)`
HSV to RGB|`hsvtorgb(hsv)`
HCL to RGB|`hcltorgb(hcl)`
Linear to sRGB (luminance)|`linear_to_srgb_luminance(input)`
Linear to sRGB|`linear_to_srgb_rgb(input)`
sRGB to Linear|`srgb_to_linear_rgb(input)`
sRGB to Linear (luminance)|`srgb_to_linear_luminance(input)`
Temprature to RGB|`temperature_to_rgb(temperature)`
Temprature to RGB Fit|`temperature_to_rgb_fit(input, a, b, c, d)`
ACEScg to Linear sRGB|`acescg_to_linear_srgb(input)`
Linear sRGB to ACEScg|`linear_srgb_to_acescg(input)`
Non Square Output Size|`non_square_output_size(scale, output_size, non_square)`
Non Square Expansion UV Scale|`non_square_expansion_uv_scale(position, non_square_expansion)`
Switch Float1 2 Inputs|`switch_float1_2_inputs(input_selection, value_1, value_2)`
Switch Float1 4 Inputs|`switch_float1_4_inputs(input_selection, value_1, value_2, value_3, value_4)`
Switch Float1 8 Inputs|`switch_float1_8_inputs(input_selection, value_1, value_2, value_3, value_4, value_5, value_6, value_7, value_8)`
Switch Float2 2 Inputs|`switch_float2_2_inputs(input_selection, value_1, value_2)`
Switch Float2 4 Inputs|`switch_float2_4_inputs(input_selection, value_1, value_2, value_3, value_4)`
Switch Float2 8 Inputs|`switch_float2_8_inputs(input_selection, value_1, value_2, value_3, value_4, value_5, value_6, value_7, value_8)`
Switch Float3 2 Inputs|`switch_float3_2_inputs(input_selection, value_1, value_2)`
Switch Float3 4 Inputs|`switch_float3_4_inputs(input_selection, value_1, value_2, value_3, value_4)`
Switch Float3 8 Inputs|`switch_float3_8_inputs(input_selection, value_1, value_2, value_3, value_4, value_5, value_6, value_7, value_8)`
Switch Float4 2 Inputs|`switch_float4_2_inputs(input_selection, value_1, value_2)`
Switch Float4 4 Inputs|`switch_float4_4_inputs(input_selection, value_1, value_2, value_3, value_4)`
Switch Float4 8 Inputs|`switch_float4_8_inputs(input_selection, value_1, value_2, value_3, value_4, value_5, value_6, value_7, value_8)`
Switch Integer1 2 Inputs|`switch_integer1_2_inputs(input_selection, value_1, value_2)`
Switch Integer1 4 Inputs|`switch_integer1_4_inputs(input_selection, value_1, value_2, value_3, value_4)`
Switch Integer1 8 Inputs|`switch_integer1_8_inputs(input_selection, value_1, value_2, value_3, value_4, value_5, value_6, value_7, value_8)`
Switch Integer2 2 Inputs|`switch_integer2_2_inputs(input_selection, value_1, value_2)`
Switch Integer2 4 Inputs|`switch_integer2_4_inputs(input_selection, value_1, value_2, value_3, value_4)`
Switch Integer2 8 Inputs|`switch_integer2_8_inputs(input_selection, value_1, value_2, value_3, value_4, value_5, value_6, value_7, value_8)`
Switch Integer3 2 Inputs|`switch_integer3_2_inputs(input_selection, value_1, value_2)`
Switch Integer3 2 Inputs|`switch_integer3_4_inputs(input_selection, value_1, value_2, value_3, value_4)`
Switch Integer3 2 Inputs|`switch_integer3_8_inputs(input_selection, value_1, value_2, value_3, value_4, value_5, value_6, value_7, value_8)`
Switch Integer4 2 Inputs|`switch_integer4_2_inputs(input_selection, value_1, value_2)`
Switch Integer4 4 Inputs|`switch_integer4_4_inputs(input_selection, value_1, value_2, value_3, value_4)`
Switch Integer4 8 Inputs|`switch_integer4_8_inputs(input_selection, value_1, value_2, value_3, value_4, value_5, value_6, value_7, value_8)`