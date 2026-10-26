#include <cassert>
#include "video_core/amdgpu/command_copy.h"
int main(){
 std::vector<u32> arena;arena.reserve(4);std::atomic<u32> offset=0;
 std::vector<u32> first{1,2,3};auto a=AmdGpu::CopyCommands(first,arena,offset);
 auto* address=arena.data();auto capacity=arena.capacity();
 std::vector<u32> burst(2*capacity+1,77);auto b=AmdGpu::CopyCommands(burst,arena,offset);
 assert(b.owner && !a.owner && arena.data()==address && arena.capacity()==capacity);
 assert(a.words[0]==1 && a.words[2]==3 && offset==3);
 burst[0]=99;assert(b.words[0]==77);
 auto retained=std::move(b.owner);assert(b.words.back()==77 && retained->size()==burst.size());
 offset=0;std::vector<u32> exact(capacity,42);auto c=AmdGpu::CopyCommands(exact,arena,offset);
 assert(!c.owner && offset==capacity && c.words.back()==42);
 auto d=AmdGpu::CopyCommands(first,arena,offset);assert(d.owner && d.words[1]==2);
 offset=static_cast<u32>(capacity+1);auto e=AmdGpu::CopyCommands(first,arena,offset);assert(e.owner);
}
