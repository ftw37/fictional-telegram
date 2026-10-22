#include <cstdio>
#include "video_core/texture_cache/types.h"

using VideoCore::SubresourceExtent;
static_assert(!SubresourceExtent{12, 1}.Contains({1, 6}));
static_assert(!SubresourceExtent{1, 6}.Contains({12, 1}));
static_assert(SubresourceExtent{12, 6}.Contains({1, 6}));
static_assert(SubresourceExtent{12, 6}.Contains({12, 1}));
static_assert(SubresourceExtent{12, 6}.Contains({12, 6}));

int main() {
    // Each mip/layer pair names a distinct addressable subresource. A cached image
    // must contain every pair requested, including crossed mip/layer dimensions.
    unsigned checks = 0;
    for (unsigned levels = 1; levels <= 16; ++levels)
        for (unsigned layers = 1; layers <= 8; ++layers)
            for (unsigned requested_levels = 1; requested_levels <= 16; ++requested_levels)
                for (unsigned requested_layers = 1; requested_layers <= 8; ++requested_layers) {
                    const SubresourceExtent available{levels, layers};
                    const SubresourceExtent requested{requested_levels, requested_layers};
                    bool all_present = true;
                    for (unsigned mip = 0; mip < requested_levels; ++mip)
                        for (unsigned layer = 0; layer < requested_layers; ++layer)
                            all_present &= mip < levels && layer < layers;
                    if (available.Contains(requested) != all_present) return 1;
                    ++checks;
                }
    std::printf("PASS: %u mip/layer containment cases\n", checks);
}
