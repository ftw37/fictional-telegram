"""Build a local, separate no-turn-vignette game view from the user's extracted copy.
No game data is distributed by this script. Original files are never modified.
"""
from pathlib import Path
import argparse,hashlib,json,os,struct,zlib

def build(source:Path,dest:Path):
 source=source.resolve(strict=True);dest=dest.resolve()
 if dest.exists():raise RuntimeError('Destination must be new')
 pak=source/'daedalus_01/content/paks/pakchunk0-ps4.pak'
 with pak.open('rb') as f:
  f.seek(-44,2);footer=f.read(44);magic,ver,off,size=struct.unpack_from('<IIQQ',footer)
  assert magic==0x5a6f12e1 and ver==3
  f.seek(off);idx=f.read(size);assert hashlib.sha1(idx).digest()==footer[24:]
  pos=0
  def unpack(fmt):
   nonlocal pos
   r=struct.unpack_from(fmt,idx,pos);pos+=struct.calcsize(fmt);return r
  def string():
   nonlocal pos
   n,=unpack('<i');assert n>0
   s=idx[pos:pos+n];pos+=n;return s[:-1].decode()
  mount=string();count,=unpack('<i');found=None
  for _ in range(count):
   name=string();o,s,u,c=unpack('<QQQI');digest=idx[pos:pos+20];pos+=20;blocks=[]
   if c:
    n,=unpack('<i');blocks=[unpack('<QQ') for j in range(n)]
   encrypted,blocksize=unpack('<BI')
   if name=='Daedalus_01/Content/Blueprints/GameMode/BP_DGPlayer.uasset':found=(name,o,s,u,c,digest,blocks,encrypted)
  assert pos==len(idx) and found
  name,o,s,u,c,digest,blocks,encrypted=found;assert not encrypted
  if c:
   assert c==1;data=b''
   for a,b in blocks:f.seek(a);data+=zlib.decompress(f.read(b-a))
  else:f.seek(o+53);data=f.read(s)
  assert len(data)==u and hashlib.sha1(data).digest()==digest
 assert hashlib.sha256(data).hexdigest()=='14bcf56aa8615a657ab13d11bc2035aa615188957a8dbf0d64c09c0f775b81c3','Unsupported game asset version'
 # This signature is the single turn-active assignment to VRPeripheryGoal,
 # followed by its interpolation-speed assignment. Do not change cinematic calls.
 sig=bytes.fromhex('0f0900000001090000001ecdcc4c3f0f0500000001050000001e9a99993d')
 assert data.count(sig)==1,'Unsupported player Blueprint; no changes made'
 at=data.index(sig)+11
 assert struct.unpack_from('<f',data,at)[0] > .79
 patched=data[:at]+struct.pack('<f',0.0)+data[at+4:]
 assert len(patched)==len(data)
 for root,dirs,files in os.walk(source):
  rel=Path(root).relative_to(source);target=dest/rel;target.mkdir(parents=True,exist_ok=True)
  for file in files:
   src=Path(root)/file;dst=target/file
   if src.suffix.lower() in ['.pak','.mp4','.bin','.prx','.sprx']:os.link(src,dst)
   else:dst.write_bytes(src.read_bytes())
 def fs(s):
  b=s.encode()+b'\0';return struct.pack('<i',len(b))+b
 entry=struct.pack('<QQQI',0,len(patched),len(patched),0)+hashlib.sha1(patched).digest()+struct.pack('<BI',0,0)
 index=fs(mount)+struct.pack('<i',1)+fs(name)+entry
 body=entry+patched
 output=body+index+struct.pack('<IIQQ',0x5a6f12e1,3,len(body),len(index))+hashlib.sha1(index).digest()
 overlay=dest/'daedalus_01/content/paks/pakchunk0-ps4_P.pak';overlay.write_bytes(output)
 report={'original_asset_sha256':hashlib.sha256(data).hexdigest(),'patched_asset_sha256':hashlib.sha256(patched).hexdigest(),'asset_offset':at,'old_turn_target':0.8,'new_turn_target':0.0,'overlay':str(overlay),'overlay_sha256':hashlib.sha256(output).hexdigest(),'original_package_unchanged':True}
 (dest/'no-turn-vignette-build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--destination',type=Path,required=True);a=p.parse_args();build(a.source,a.destination)
