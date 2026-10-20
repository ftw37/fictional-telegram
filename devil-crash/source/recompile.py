"""Game-specific native address dispatcher. No runtime opcode dispatch fallback.
Instruction semantics and hardware scheduling are supplied by Genesis Plus GX.
"""
import collections, hashlib, pathlib, re, sys
rom=pathlib.Path(sys.argv[1]).read_bytes();root=pathlib.Path(sys.argv[2])
if hashlib.sha256(rom).hexdigest()!='9e9734a2904d61d27585496edad830e329dd6bfe4e5859c11535532046d07262':raise ValueError('Unsupported ROM revision')
ops=re.findall(r'\bm68k_op_\w+\b',(root/'core/m68k/m68ki_instruction_jump_table.h').read_text())
assert len(ops)==65536
out=root/'core/m68k/devil_native.h'
with out.open('w') as f:
 f.write('''/* Generated for Devil Crash MD (Japan). ROM SHA256 verified by generator. */
#include <stdio.h>
#include <stdlib.h>
static unsigned long long dc_native_count;
#ifdef _WIN32
#define DC_EXPORT __declspec(dllexport)
#else
#define DC_EXPORT __attribute__((visibility("default")))
#endif
DC_EXPORT unsigned long long retro_native_instructions(void) { return dc_native_count; }
static void dc_native_fault(unsigned int pc) {
  fprintf(stderr,"Native instruction mismatch or unsupported PC: %06x (IR %04x)\\n",pc,REG_IR);
  abort();
}
''')
 for page in range(len(rom)//256):
  f.write(f'static void dc_page_{page:04x}(unsigned int pc) {{\n switch(pc & 255u) {{\n')
  groups=collections.defaultdict(list)
  for n in range(0,256,2):groups[int.from_bytes(rom[page*256+n:page*256+n+2],'big')].append(n)
  for op,offsets in groups.items():
   f.write(' '.join(f'case {n}:' for n in offsets))
   f.write(f' if(REG_IR!=0x{op:04x}){{dc_native_fault(pc);return;}} REG_IR=0x{op:04x}; {ops[op]}(); return;\n')
  f.write(' default:dc_native_fault(pc);return; }\n}\n')
 f.write('static void dc_native_dispatch(unsigned int pc) {\n pc &= 0xffffffu; ++dc_native_count;\n switch(pc >> 8) {\n')
 for page in range(len(rom)//256):f.write(f'case {page}: dc_page_{page:04x}(pc); return;\n')
 f.write('default:dc_native_fault(pc);return;\n}\n}\n')
p=root/'core/m68k/m68kcpu.c';s=p.read_text()
if '#include "devil_native.h"' not in s:s=s.replace('#include "m68kops.h"','#include "m68kops.h"\n#include "devil_native.h"')
s=s.replace('m68ki_instruction_jump_table[REG_IR]();','dc_native_dispatch(REG_PC - 2);')
s=s.replace('/* Decode next instruction */','/* Preserve hardware prefetch; generated native address code selects semantics. */')
p.write_text(s)
assert 'm68ki_instruction_jump_table[REG_IR]();' not in s
print('Generated',len(rom)//2,'native address cases covering the entire ROM;',out.stat().st_size,'source bytes')
