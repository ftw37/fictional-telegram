// SPDX-License-Identifier: GPL-2.0-or-later
// Synthetic metadata only: no game audio is included.
#include "core/libraries/ngs2/ngs2_waveform.h"
#include <cassert>
#include <iostream>
#include <vector>
using namespace Libraries::Ngs2;
using Bytes = std::vector<u8>;
void Set16(Bytes &b, size_t at, u16 n) {
  b[at] = u8(n);
  b[at + 1] = u8(n >> 8);
}
void Set32(Bytes &b, size_t at, u32 n) {
  for (int i = 0; i < 4; ++i)
    b[at + i] = u8(n >> (i * 8));
}
void Chunk(Bytes &b, const char *id, const Bytes &data) {
  const auto at = b.size();
  b.resize(at + 8);
  std::memcpy(b.data() + at, id, 4);
  Set32(b, at + 4, u32(data.size()));
  b.insert(b.end(), data.begin(), data.end());
  if (data.size() & 1)
    b.push_back(0);
}
Bytes Wave(const Bytes &fmt, const Bytes &data, const Bytes &fact = {}) {
  Bytes b(12);
  std::memcpy(b.data(), "RIFF", 4);
  std::memcpy(b.data() + 8, "WAVE", 4);
  Chunk(b, "JUNK", {42});
  Chunk(b, "fmt ", fmt);
  if (!fact.empty())
    Chunk(b, "fact", fact);
  Chunk(b, "data", data);
  Set32(b, 4, u32(b.size() - 8));
  return b;
}
int main() {
  Bytes pcm(16);
  Set16(pcm, 0, 1);
  Set16(pcm, 2, 2);
  Set32(pcm, 4, 48000);
  Set32(pcm, 8, 192000);
  Set16(pcm, 12, 4);
  Set16(pcm, 14, 16);
  auto wave = Wave(pcm, Bytes(160));
  auto parsed = Waveform::Parse(wave);
  assert(parsed && parsed->samples == 40 && parsed->format.type == 0x12 &&
         parsed->bytes == 160);
  auto block = Waveform::CalculateBlock(parsed->format, 7, 13);
  assert(block && block->offset == 28 && block->bytes == 52 &&
         block->skip == 0 && block->samples == 13);
  assert(!Waveform::CalculateBlock(parsed->format, 0, 0));
  assert(!Waveform::CalculateBlock(parsed->format, 0, 0xffffffff));
  for (size_t length = 0; length < wave.size(); ++length)
    assert(!Waveform::Parse(std::span<const u8>(wave).first(length)));
  auto malformed = wave;
  Set32(malformed, 16, 0xffffffff);
  assert(!Waveform::Parse(malformed));
  Bytes at9(52);
  Set16(at9, 0, 0xfffe);
  Set16(at9, 2, 2);
  Set32(at9, 4, 48000);
  Set32(at9, 8, 24000);
  Set16(at9, 12, 512);
  Set16(at9, 16, 34);
  Set16(at9, 18, 1024);
  Set32(at9, 20, 3);
  const u8 guid[]{0xd2, 0x42, 0xe1, 0x47, 0xba, 0x36, 0x8d, 0x4d,
                  0x88, 0xfc, 0x61, 0x65, 0x4f, 0x8c, 0x83, 0x6c};
  std::memcpy(at9.data() + 24, guid, 16);
  Set32(at9, 40, 1);
  at9[44] = 0xfe;
  at9[45] = 0x74;
  at9[46] = 0x0f;
  at9[47] = 0xf0;
  Bytes fact(12);
  Set32(fact, 0, 1000);
  Set32(fact, 4, 256);
  Set32(fact, 8, 256);
  auto compressed = Wave(at9, Bytes(1024), fact);
  auto info = Waveform::Parse(compressed);
  assert(info && info->format.type == 0x40 &&
         info->format.config == 0xfe740ff0);
  assert(info->layout.bytes == 512 && info->layout.samples == 1024 &&
         info->layout.units == 4);
  assert(info->format.delay == 256 && info->samples == 1000 &&
         info->layout.delay == 256);
  assert(info->offset == 110); // Includes the padded JUNK chunk, fmt and fact headers.
  auto whole = Waveform::CalculateBlock(info->format, 0, 1000);
  assert(whole && whole->offset == 0 && whole->bytes == 1024 &&
         whole->skip == 256);
  auto seek = Waveform::CalculateBlock(info->format, 1024, 100);
  assert(seek && seek->offset == 0 && seek->bytes == 1024 &&
         seek->skip == 1280);
  for (size_t length = 0; length < compressed.size(); ++length)
    assert(!Waveform::Parse(std::span<const u8>(compressed).first(length)));
  auto badfmt = at9;
  badfmt[24] ^= 1;
  assert(!Waveform::Parse(Wave(badfmt, Bytes(1024), fact)));
  badfmt = at9;
  badfmt[44] = 0;
  assert(!Waveform::Parse(Wave(badfmt, Bytes(1024), fact)));
  badfmt = at9;
  badfmt[45] = 0x7c; // Invalid ATRAC9 channel-table index six.
  assert(!Waveform::Parse(Wave(badfmt, Bytes(1024), fact)));
  badfmt = at9;
  Set16(badfmt, 2, 9);
  assert(!Waveform::Parse(Wave(badfmt, Bytes(1024), fact)));
  auto badfact = fact;
  Set32(badfact, 0, 4000);
  assert(!Waveform::Parse(Wave(at9, Bytes(1024), badfact)));
  std::cout << "PASS: PCM/ATRAC9 metadata, padding, seeks, overflow, malformed "
               "chunks and all truncated prefixes\n";
}
