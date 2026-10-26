#include <cassert>
#include <limits>
#include <vector>
#include <cmath>
#include "core/libraries/audio/audio_safety.h"
using Libraries::AudioOut::AudioSafety;
int main() {
 AudioSafety a; std::vector<float> x{4,-2,0,1}; a.Process(x,2,48000);
 assert(std::abs(x[0]-.25f)<1e-6f && std::abs(x[1]+.125f)<1e-6f);
 AudioSafety b; std::vector<float> y{NAN,INFINITY,-INFINITY,.1f}; b.Process(y,2,48000);
 assert(y[0]==0 && y[1]==0 && y[2]==0 && std::abs(y[3]-.1f)<1e-6f);
 for(int k=0;k<1000;k++){x={float(k%31)*.2f,-float(k%31)*.1f};a.Process(x,1,48000);for(float v:x)assert(std::isfinite(v)&&std::abs(v)<=.25001f);}
 AudioSafety c; std::vector<s16> z{-32768,16384};c.Process(z,1,48000);assert(z[0]==-8192&&z[1]==4096);
 AudioSafety d; std::vector<float> silence(1024);d.Process(silence,512,48000);for(float v:silence)assert(v==0);
}
