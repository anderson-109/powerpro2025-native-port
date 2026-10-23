#include "../pad_axis.h"
#include <assert.h>
#include <stdio.h>
int main(void) {
    assert(dm_pad_axis(0, 0) == 0);
    assert(dm_pad_axis(1, 0) == 32767 && dm_pad_axis(-1, 0) == -32767);
    assert(dm_pad_axis(2, .1f) == 32767 && dm_pad_axis(-2, .1f) == -32767);
    assert(dm_pad_axis(NAN, 0) == 0 && dm_pad_axis(INFINITY, 0) == 0);
    assert(dm_pad_axis(.1f, .1f) == 0 && dm_pad_axis(-.1f, .1f) == 0);
    assert(dm_pad_axis(.55f, .1f) == 16384 && dm_pad_axis(-.55f, .1f) == -16384);
    int32_t last = 0;
    for (int i = 0; i <= 10000; ++i) {
        float v = (float)i / 10000;
        int32_t a = dm_pad_axis(v, .1f);
        assert(a >= last && a <= 32767 && dm_pad_axis(-v, .1f) == -a); last = a;
    }
    assert(dm_pad_axis(.5f, NAN) == dm_pad_axis(.5f, 0));
    puts("controller axis endpoints, clipping, deadzone, finite values, symmetry and monotonicity passed");
}
