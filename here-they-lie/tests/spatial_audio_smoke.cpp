#include <cassert>
#include <cmath>
#include <vector>
#include "core/libraries/audio3d/audio3d_spatializer.h"
using namespace Libraries::Audio3d;
std::vector<float> render(float x) {
 Spatializer s; ObjectPlacement p; p.x=x;p.z=-1;p.gain=.1f;
 std::vector<float> out(8192), in(4096);
 for(int i=0;i<4096;i++)in[i]=std::sin(i*0.43f);
 s.Process(in.data(),4096,out.data(),p,48000);return out;
}
int main(){
 auto left=render(-2),right=render(2),center=render(0);
 double el=0,er=0;
 for(int i=100;i<4096;i++){
  assert(std::abs(left[2*i]-right[2*i+1])<1e-5);
  assert(std::abs(left[2*i+1]-right[2*i])<1e-5);
  assert(std::abs(center[2*i]-center[2*i+1])<1e-5);
  el+=left[2*i]*left[2*i];er+=left[2*i+1]*left[2*i+1];
 }
 assert(el>er); // A left source must favor the left ear.
 Spatializer silent; ObjectPlacement p; std::vector<float> input(512,1),output(1024);
 silent.Process(input.data(),512,output.data(),p,48000);for(float v:output)assert(v==0);
}
