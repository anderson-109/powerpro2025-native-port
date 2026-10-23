#pragma once
#include <math.h>
#include <stdint.h>
// Finite GameController values become Horizon signed stick samples. The optional
// calibrated front-end deadzone rescales the remaining travel continuously.
static inline int32_t dm_pad_axis(float value, float deadzone) {
    if (!isfinite(value)) return 0;
    float v = fmaxf(-1.f, fminf(1.f, value));
    if (!isfinite(deadzone) || deadzone < 0 || deadzone >= .5f) deadzone = 0;
    if (fabsf(v) <= deadzone) return 0;
    return (int32_t)lrintf(copysignf((fabsf(v) - deadzone) / (1.f - deadzone), v) * 32767.f);
}
