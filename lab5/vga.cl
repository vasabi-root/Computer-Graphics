__inline float4 prod(
    __constant float *matrix,
    float4 vec
)
{
    float4 p;
    for (int i = 0; i < 4; i++)
    {
        p[i] = 0;
        for (int j = 0; j < 4; j++)
        {
            p[i] += matrix[i*4 + j]*vec[j];
        }
    }
    return p;
}

__inline float computeLightForDot(
    __constant float *light_g,
    __const float intensity,
    __const float4 P,
    __const float4 N
)
{
    float i = 1 - intensity;
    float4 L = (float4)(light_g[0]-P[0], light_g[1]-P[1], light_g[2]-P[2], light_g[3]-P[3]);
    float N_dot_L = N[0]*L[0] + N[1]*L[1] + N[2]*L[2];
    if (N_dot_L > 0)
    {
        i += intensity*N_dot_L / (fast_length(N) * fast_length(L));
    }
    return i;
}

__kernel void computeLightForSphere(
    __constant int *size_g,
    __constant float *coords_g,  // 4 x 1 
    __constant float *screen_g,  // 4 x 1 
    __constant float *reverse_g, // 4 x 4 = 16 x 1
    __constant float *R_g,
    __constant float *step_g,
    __constant int *color_g,
    __constant float *light_g,   // 4 x 1
    __constant float *intensity_g,
    __global float4 *pix_g,      // 1 x 1 float 4 = 1 x 4
    __global int4 *computed_color_g
)
{
    int i = get_global_id(0);
    int j = get_global_id(1);
    // printf("i = %d, j = %d, local = %d\n", i,j,get_local_id(0));
    int index = i*(*size_g)+j;
    float theta = i*(*step_g) + 3.1415/2;
    float fi = index * (*step_g);

    // printf("size = %d\n", *size_g);
    // printf("coords = [%f %f %f %f]\n", coords_g[0], coords_g[1], coords_g[2], coords_g[3]);
    // printf("screen = [%f %f %f %f]\n", screen_g[0], screen_g[1], screen_g[2], screen_g[3]);
    // printf("R = %f\n", *R_g);
    // printf("step = %f\n", *step_g);
    // printf("color = [%d %d %d %d]\n", color_g[0], color_g[1], color_g[2], color_g[3]);
    // printf("light = [%f %f %f %f]\n", light_g[0], light_g[1], light_g[2], light_g[3]);
    // printf("intensity = %f\n", *intensity_g);


    float4 P_screen;

    P_screen[0] = screen_g[0] + (*R_g)*native_sin(theta)*native_cos(fi);
    P_screen[1] = screen_g[1] + (*R_g)*native_sin(theta)*native_sin(fi);
    P_screen[2] = screen_g[2] + (*R_g)*native_cos(theta);
    P_screen[3] = 1;

    float4 P = prod(reverse_g, P_screen);
    float4 N = (float4)(P[0] - coords_g[0], P[1] - coords_g[1], P[2] - coords_g[2], P[3] - coords_g[3]);
    float inten = computeLightForDot(light_g, *intensity_g, P, N);
    // printf("i = %f\n", inten);

    pix_g[index] = P_screen;
    // printf("P = [%f %f %f %f] \n", P[0], P[1],P[2],P[3]);
    computed_color_g[index] = (int4)((int)(color_g[0] * inten), (int)(color_g[1] * inten), (int)(color_g[2] * inten), (int)(color_g[3]));
}