"""Debugger-assisted capture and optional experimental tracker-format translation.

A temporary software breakpoint is restored before the local test process exits.
The emulator and game files are not modified.
"""
import ctypes as C,struct,os,json,time,sys,hashlib
from ctypes import wintypes as W
from pathlib import Path
k=C.WinDLL('kernel32',use_last_error=True)
def fn(name,args,ret=W.BOOL):
 f=getattr(k,name);f.argtypes=args;f.restype=ret;return f
create=fn('CreateProcessW',[W.LPCWSTR,W.LPWSTR,C.c_void_p,C.c_void_p,W.BOOL,W.DWORD,C.c_void_p,W.LPCWSTR,C.c_void_p,C.c_void_p])
wait=fn('WaitForDebugEvent',[C.c_void_p,W.DWORD])
cont=fn('ContinueDebugEvent',[W.DWORD,W.DWORD,W.DWORD])
read=fn('ReadProcessMemory',[W.HANDLE,C.c_void_p,C.c_void_p,C.c_size_t,C.c_void_p])
write=fn('WriteProcessMemory',[W.HANDLE,C.c_void_p,C.c_void_p,C.c_size_t,C.c_void_p])
protect=fn('VirtualProtectEx',[W.HANDLE,C.c_void_p,C.c_size_t,W.DWORD,C.c_void_p])
flush=fn('FlushInstructionCache',[W.HANDLE,C.c_void_p,C.c_size_t])
thread=fn('OpenThread',[W.DWORD,W.BOOL,W.DWORD],W.HANDLE)
getctx=fn('GetThreadContext',[W.HANDLE,C.c_void_p])
setctx=fn('SetThreadContext',[W.HANDLE,C.c_void_p])
alloc=fn('VirtualAllocEx',[W.HANDLE,C.c_void_p,C.c_size_t,W.DWORD,W.DWORD],C.c_void_p)
detach=fn('DebugActiveProcessStop',[W.DWORD])
terminate=fn('TerminateProcess',[W.HANDLE,W.UINT])
close=fn('CloseHandle',[W.HANDLE])
def check(ok):
 if not ok:raise C.WinError(C.get_last_error())
def mem(handle,address,n):
 b=C.create_string_buffer(n);check(read(handle,address,b,n,None));return b.raw
def put(handle,address,b):
 old=W.DWORD();check(protect(handle,address,len(b),0x40,C.byref(old)))
 check(write(handle,address,C.c_char_p(b),len(b),None));check(flush(handle,address,len(b)))
 check(protect(handle,address,len(b),old.value,C.byref(old)))

root=Path(os.environ.get('HTL_TEST_ROOT', str(Path.home()/'Documents/Codex/HTL-Test')))
exe=root/'pc-vr/shadps4.exe'
assert hashlib.sha256(exe.read_bytes()).hexdigest()=='e5d5233aa920781d1e92e6745e9a994591c8088d9e827cd905558b27054e20c8'
pid=int((root/'tools/adapted-test-pid.txt').read_text())
openprocess=fn('OpenProcess',[W.DWORD,W.BOOL,W.DWORD],W.HANDLE)
attach=fn('DebugActiveProcess',[W.DWORD])
killonexit=fn('DebugSetProcessKillOnExit',[W.BOOL])
process=openprocess(0x1fffff,False,pid);check(process)
check(attach(pid));check(killonexit(False))
event=C.create_string_buffer(176);bp=None;original=None;pending=None;installed=False
try:
 deadline=time.monotonic()+20
 while time.monotonic()<deadline:
  if not wait(event,1000):continue
  code,epid,etid=struct.unpack_from('<III',event.raw);pending=(epid,etid);status=0x10002
  if code==3:
   base=struct.unpack_from('<Q',event.raw,40)[0];bp=base+0xb45060
   original=mem(process,bp,19)
   assert original==bytes.fromhex('5541574156415541545657534881ecc8030000')
   put(process,bp,b'\xcc')
  elif code==1:
   exception=struct.unpack_from('<I',event.raw,16)[0];address=struct.unpack_from('<Q',event.raw,32)[0]
   if exception==0x80000003 and address==bp:
    th=thread(0x1fffff,False,etid);check(th)
    storage=C.create_string_buffer(1264);aligned=(C.addressof(storage)+15)&~15
    C.memset(aligned,0,1232);C.c_uint32.from_address(aligned+48).value=0x100003
    check(getctx(th,aligned))
    span=C.c_uint64.from_address(aligned+184).value
    pointer,count=struct.unpack('<QQ',mem(process,span,16))
    frame=C.c_uint64.from_address(aligned+192).value
    print('span',hex(pointer),count,'region',mem(process,pointer,48).hex(),'frame',mem(process,frame,32).hex(),flush=True)
    assert count==2, 'Expected original stereo presentation'
    region=mem(process,pointer,96)
    assert region[40]==0 and region[88]==0
    assert region[:8]==region[48:56], 'Only support shared-image stereo submissions'
    remote=alloc(process,None,4096,0x3000,0x40);check(remote)
    control=remote+0x800
    put(process,control,struct.pack('<I',1))
    stub=bytearray(bytes.fromhex('9c50415241534d8b104983780802'))
    branches=[]
    def branch(op):
     stub.extend(bytes([op,0]));branches.append(len(stub)-1)
    branch(0x75)
    # Both submissions must use the same source image.
    stub.extend(bytes.fromhex('498b0249394230'));branch(0x75)
    stub.extend(b'\x49\xbb'+struct.pack('<Q',control))
    stub.extend(bytes.fromhex('41833b00'));branch(0x74)
    # Preserve the old rectangle as scissor; expand the image viewport to the
    # whole stereo output. Each draw now samples only its corresponding half.
    for offset in (0,48):
     for src,dst in ((8,24),(12,28),(16,32),(20,36)):
      stub.extend(bytes([0x41,0x8b,0x42,src+offset,0x41,0x89,0x42,dst+offset]))
     stub.extend(bytes([0x41,0xc6,0x42,40+offset,1]))
     stub.extend(bytes([0x41,0xc7,0x42,8+offset,0,0,0,0]))
     stub.extend(bytes([0x41,0xd1,0x62,16+offset]))
    done=len(stub)
    for at in branches:
     assert done-at-1<128
     stub[at]=done-at-1
    stub.extend(bytes.fromhex('415b415a589d'))
    stub.extend(original)
    stub.extend(bytes.fromhex('ff2500000000')+struct.pack('<Q',bp+19))
    put(process,remote,bytes(stub))
    detour=bytes.fromhex('ff2500000000')+struct.pack('<Q',remote)+b'\x90'*5
    put(process,bp,detour);installed=True
    Path(__file__).with_name('stereo-sampling-state.json').write_text(json.dumps({'pid':pid,'entry':bp,'control':control,'remote':remote,'original':original.hex(),'stub':stub.hex()},indent=2))
    print('Shared-image half-eye sampling enabled; control',hex(control),flush=True)
    C.c_uint64.from_address(aligned+248).value=bp;check(setctx(th,aligned));close(th)
    check(cont(epid,etid,status));pending=None
    break
   elif exception!=0x80000003:status=0x80010001
  check(cont(epid,etid,status));pending=None
 else:raise TimeoutError('postprocessing call not reached')
finally:
 if bp and original and not installed:put(process,bp,original)
 if pending:cont(*pending,0x10002)
 check(detach(pid));close(process)
