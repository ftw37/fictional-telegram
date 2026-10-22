#include <algorithm>
#include <cstdio>
#include <vector>
#include "core/vr/htl_timing.h"
int main() {
    using namespace Core::Vr;
    std::vector<u8> image(HtlFrameCapSite + HtlFrameCapOriginal.size() + 16, 0xa5);
    if (ApplyHtlFrameCapBypass({})) return 1;
    if (ApplyHtlFrameCapBypass(std::span<u8>{image}.first(HtlFrameCapSite + 25))) return 2;
    auto site = image.data() + HtlFrameCapSite;
    for (size_t i=0; i<HtlFrameCapOriginal.size(); ++i) {
        std::copy(HtlFrameCapOriginal.begin(), HtlFrameCapOriginal.end(), site);
        site[i] ^= 1;
        const std::vector<u8> before=image;
        if (ApplyHtlFrameCapBypass(image) || image != before) return 3;
    }
    std::copy(HtlFrameCapOriginal.begin(), HtlFrameCapOriginal.end(), site);
    const std::vector<u8> before=image;
    if (!ApplyHtlFrameCapBypass(image)) return 4;
    int original_displacement{}, patched_displacement{};
    std::memcpy(&original_displacement, before.data()+HtlFrameCapSite+10,4);
    std::memcpy(&patched_displacement, site+9,4);
    if (14+original_displacement != 13+patched_displacement) return 5;
    for(size_t i=0;i<image.size();++i) {
        if ((i<HtlFrameCapSite+8 || i>=HtlFrameCapSite+14) && image[i]!=before[i]) return 6;
    }
    if (ApplyHtlFrameCapBypass(image)) return 7;
    std::puts("PASS: truncated/mutated signatures rejected without writes; branch target and surrounding bytes preserved");
}
