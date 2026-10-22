#include <bit>
#include <iterator>
#include <random>
#include <cstdio>
#include "common/bit_array.h"
int main() {
    Common::BitArray<1024> bits;
    std::mt19937_64 random(12345);
    unsigned checks = 0;
    for (unsigned pattern = 0; pattern < 24; ++pattern) {
        bits.Clear();
        for (size_t i = 0; i < 1024; ++i) {
            if ((pattern == 1) || (pattern > 1 && random() % (pattern * 4) == 0)) bits.Set(i);
        }
        for (size_t start = 0; start <= 1025; ++start) {
            for (size_t end = start; end <= 1025; ++end) {
                Common::BitArray<1024> reference(bits, start, end);
                if (bits.Any(start, end) != reference.Any()) {
                    std::printf("Mismatch %u %zu %zu\n", pattern, start, end); return 1;
                }
                ++checks;
            }
        }
        if (bits.Any(100, 10)) return 2;
    }
    std::printf("Passed %u bit-range equivalence checks\n", checks);
}
