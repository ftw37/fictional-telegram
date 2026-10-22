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

event=C.create_string_buffer(176);pending=None
try:
 deadline=time.monotonic()+180
 while time.monotonic()<deadline:
  if not wait(event,1000):continue
  code,epid,etid=struct.unpack_from('<III',event.raw);pending=(epid,etid);status=0x10002
  if code==1:
   exception=struct.unpack_from('<I',event.raw,16)[0];address=struct.unpack_from('<Q',event.raw,32)[0]
   if exception!=0x80000003:status=0x80010001
   if address==0x80ad66e34:
    th=thread(0x1fffff,False,etid);check(th)
    storage=C.create_string_buffer(1264);aligned=(C.addressof(storage)+15)&~15
    C.memset(aligned,0,1232);C.c_uint32.from_address(aligned+48).value=0x100003
    check(getctx(th,aligned));report={'exception':hex(exception),'address':hex(address),'memory':{}}
    for name,offset in [('rax',120),('rcx',128),('rdx',136),('rsi',168),('rdi',176)]:
     pointer=C.c_uint64.from_address(aligned+offset).value
     try:
      data=mem(process,pointer,2048)
      report['memory'][name]={'address':hex(pointer),'hex':data.hex(),'ascii':data.decode('utf-8',errors='replace'),'wide':data.decode('utf-16le',errors='replace')}
     except OSError:report['memory'][name]={'address':hex(pointer),'unreadable':True}
    Path(__file__).with_name('loading-trap-memory.json').write_text(json.dumps(report,indent=2))
    close(th);print('Captured loading trap arguments',flush=True)
    check(cont(epid,etid,status));pending=None;break
  elif code==5:
   print('Process exited',flush=True);break
  check(cont(epid,etid,status));pending=None
finally:
 if pending:cont(*pending,0x10002)
 detach(pid);close(process)
