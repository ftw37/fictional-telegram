#include <cassert>
#include <iostream>
#include "core/vr/theatre_mode.h"
int main() {
    using namespace Core::Vr;
    if (!TheatreEnabled()) {
        assert(PresentationState() == 0);
        SetTheatre(true);
        assert(PresentationState() == 0);
    } else {
        const auto startup = PresentationState();
        assert(IsTheatre(startup));
        SetTheatre(true);
        assert(PresentationState() == startup);
        SetTheatre(false);
        const auto stereo = PresentationState();
        assert(!IsTheatre(stereo) && stereo != startup);
        SetTheatre(false);
        assert(PresentationState() == stereo);
        SetTheatre(true);
        const auto loading = PresentationState();
        assert(IsTheatre(loading) && loading != startup && loading != stereo);
        SetTheatre(false);
        assert(!IsTheatre(PresentationState()) && PresentationState() != stereo);
    }
    std::cout << "PASS: theatre opt-in, startup, repeated requests, loading return, stale-frame generations\n";
}
