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

root=Path(os.environ.get('HTL_TEST_ROOT', str(Path.home()/'Documents/Codex/HTL-Test')));exe=root/'pc-vr/shadps4.exe'
expected='e5d5233aa920781d1e92e6745e9a994591c8088d9e827cd905558b27054e20c8'
if hashlib.sha256(exe.read_bytes()).hexdigest()!=expected:
 raise RuntimeError('This diagnostic only supports the verified AstroQuest 0.23 emulator. No process was started.')
os.environ.update(SHADPS4_OPENXR='0',SHADPS4_XR_WAIT='0',SHADPS4_VR_DEMO=('0' if '--stationary' in sys.argv else '1'),SHADPS4_VR_DESKTOP_VIEW='spectator')
startup=C.create_string_buffer(104);struct.pack_into('<I',startup,0,104)
pi=C.create_string_buffer(24)
cmd=C.create_unicode_buffer(f'"{exe}" -g "{root}/game/uroot/eboot.bin" --ignore-game-patch --fullscreen false')
check(create(str(exe),cmd,None,None,False,2,None,str(root/'pc-vr'),startup,pi))
process,mainthread,pid,tid=struct.unpack('<QQII',pi.raw)
event=C.create_string_buffer(176);bp=None;original=None;detached=False;init_done=False
deadline=time.monotonic()+90
try:
 while time.monotonic()<deadline:
  if not wait(event,1000):continue
  code,epid,etid=struct.unpack_from('<III',event.raw)
  status=0x10002
  if code==3:
   base=struct.unpack_from('<Q',event.raw,16+24)[0];bp=base+0x82a820
   if '--rotation-only' in sys.argv:
    for offset,expected_bytes in ((0x83fbf9,bytes.fromhex('c5fa110e')),(0x83fc3d,bytes.fromhex('c5fa11461c'))):
     assert mem(process,base+offset,len(expected_bytes))==expected_bytes
     put(process,base+offset,b'\x90'*len(expected_bytes))
    print('Rotation-only active: fixed head center and zero linear velocity',flush=True)
   original=mem(process,bp,1);assert original==b'\x55',original.hex()
   put(process,bp,b'\xcc');print('Tracker breakpoint installed',hex(bp),flush=True)
  elif code==1:
   exception=struct.unpack_from('<I',event.raw,16)[0]
   address=struct.unpack_from('<Q',event.raw,16+16)[0]
   if exception==0x80000003 and address==bp:
    th=thread(0x1fffff,False,etid);check(th)
    storage=C.create_string_buffer(1264);aligned=(C.addressof(storage)+15)&~15
    C.memset(aligned,0,1232);C.c_uint32.from_address(aligned+48).value=0x100003
    check(getctx(th,aligned));rdi=C.c_uint64.from_address(aligned+176).value
    if init_done:
     observed=struct.unpack('<I',mem(process,rdi,4))[0]
     Path(__file__).with_name('gpu-submit-arguments.json').write_text(json.dumps({'size':observed,'header':mem(process,rdi,64).hex()},indent=2))
     print('GPU submit observed size',hex(observed),'host expects 0x288',flush=True)
     assert observed==0x228, "Unexpected tracker GPU structure size"
     # This host implementation only checks the size; it consumes no camera data.
     # Preserve its initialization, pointer and headset checks, accepting this
     # observed legacy size in this temporary test process only.
     assert mem(process,base+0x8323eb,6)==bytes.fromhex('813f88020000')
     put(process,base+0x8323ed,struct.pack('<I',observed))
     put(process,bp,original)
     C.c_uint64.from_address(aligned+248).value=bp
     check(setctx(th,aligned));close(th)
     check(cont(epid,etid,status));check(detach(pid));detached=True
     Path(__file__).with_name('adapted-test-pid.txt').write_text(str(pid))
     print('Applied observed-size GPU submit compatibility; PID',pid,flush=True)
     break
    b=mem(process,rdi,144);result={f'{i:02x}':f'{struct.unpack_from("<I",b,i)[0]:08x}' for i in range(0,144,4)}
    Path(__file__).with_name('tracker-init-arguments.json').write_text(json.dumps(result,indent=2))
    print('INIT_ARGUMENTS',json.dumps(result),flush=True)
    put(process,bp,original)
    if '--adapt' in sys.argv:
     assert struct.unpack_from('<I',b)[0]==144
     adapted=bytearray(128);adapted[:40]=b[:40];struct.pack_into('<I',adapted,0,128)
     # Synthetic tracking does not run the camera-calibration GPU pipeline.
     # Normalize calibration to the host's supported modes, retaining allocation
     # requirements. Pointers, sizes, alignments and queue identifiers are kept.
     onion_size=struct.unpack_from('<I',b,0x48)[0]
     assert onion_size in (0x400000,0x800000)
     struct.pack_into('<I',adapted,0x30,1 if onion_size==0x800000 else 0)
     adapted[0x48:0x80]=b[0x40:0x78]
     assert struct.unpack_from('<I',adapted,0x60)[0]==0x3000000
     assert struct.unpack_from('<I',adapted,0x70)[0]==0x1000000
     remote=alloc(process,None,4096,0x3000,4);check(remote)
     check(write(process,remote,C.c_char_p(bytes(adapted)),len(adapted),None))
     C.c_uint64.from_address(aligned+176).value=remote
     C.c_uint64.from_address(aligned+248).value=bp
     check(setctx(th,aligned));close(th)
     if '--gpu-compat' in sys.argv:
      init_done=True;bp=base+0x8323c0;original=mem(process,bp,1)
      assert original==b'\x48'
      put(process,bp,b'\xcc')
      check(cont(epid,etid,status))
      continue
     check(cont(epid,etid,status));check(detach(pid));detached=True
     Path(__file__).with_name('adapted-test-pid.txt').write_text(str(pid))
     print('Applied temporary 144-to-128-byte tracker translation; PID',pid,flush=True)
    else:close(th)
    break
   elif exception!=0x80000003:status=0x80010001
  elif code==5:raise RuntimeError('Emulator exited before tracker initialization')
  check(cont(epid,etid,status))
 else:raise TimeoutError('Tracker initialization not reached within 90 seconds')
finally:
 if not detached:terminate(process,0);cont(pid,tid,0x10002)
 close(process);close(mainthread)
