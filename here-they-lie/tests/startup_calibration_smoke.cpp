#include <cassert>
#include <iostream>
#include "core/vr/startup_calibration.h"

int main() {
    using Core::Vr::StartupCalibration;
    StartupCalibration normal;
    int held = 0;
    for (int i = 0; i < 2000; ++i) {
        const bool down = normal.Update(i * 0.01, true);
        if (i < 299 || i > 501) assert(!down);
        held += down;
    }
    assert(held >= 199 && held <= 201);
    assert(!normal.Update(1000, true));

    StartupCalibration unfocused;
    for (int i = 0; i < 250; ++i) assert(!unfocused.Update(i * 0.01, true));
    assert(!unfocused.Update(10, false));
    for (int i = 0; i < 250; ++i) assert(!unfocused.Update(20 + i * 0.01, true));

    StartupCalibration interrupted;
    for (int i = 0; i < 350; ++i) interrupted.Update(i * 0.01, true);
    assert(!interrupted.Update(4, false));
    for (int i = 0; i < 2000; ++i) assert(!interrupted.Update(10 + i * 0.01, true));

    StartupCalibration stalled;
    assert(!stalled.Update(0, true));
    assert(!stalled.Update(1000, true));
    std::cout << "PASS: one startup hold, release, focus countdown reset, no retry after interruption, no clock-gap skip\n";
}
