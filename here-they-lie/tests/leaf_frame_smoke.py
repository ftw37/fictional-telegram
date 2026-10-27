import ctypes as C,struct
k=C.WinDLL('kernel32',use_last_error=True);k.VirtualAlloc.argtypes=[C.c_void_p,C.c_size_t,C.c_ulong,C.c_ulong];k.VirtualAlloc.restype=C.c_void_p;k.VirtualFree.argtypes=[C.c_void_p,C.c_size_t,C.c_ulong]
base=k.VirtualAlloc(None,4096,0x3000,0x40);assert base
try:
 prologue=bytes.fromhex('554889e5415741564155415453');epilogue=bytes.fromhex('5b415c415d415e415f5dc3');cookie=0x123456789abcdef
 body=bytes.fromhex('48b8')+struct.pack('<Q',cookie)+bytes.fromhex('48894598')
 # Simulate scratch writes below actual RSP, as a host dispatcher can perform.
 for off in range(-8,-129,-8):body+=bytes.fromhex('48c74424')+bytes([off&255])+b'\0'*4
 body+=bytes.fromhex('488b4598')
 original=prologue+body+epilogue;exit_at=len(prologue)+len(body);C.memmove(base,original,len(original));fn=C.CFUNCTYPE(C.c_uint64)(base)
 assert fn()==0,'Unprotected case did not reproduce local loss'
 def jump(fr,to):return b'\xe9'+struct.pack('<i',to-fr-5)
 enter_stub=base+1024;data=prologue+bytes.fromhex('488da42480ffffff');data+=jump(enter_stub+len(data),base+13);C.memmove(enter_stub,data,len(data))
 exit_stub=base+1200;data=bytes.fromhex('488da42480000000')+epilogue[:5];data+=jump(exit_stub+len(data),base+exit_at+5);C.memmove(exit_stub,data,len(data))
 C.memmove(base,jump(base,enter_stub)+b'\x90'*8,13);C.memmove(base+exit_at,jump(base+exit_at,exit_stub),5)
 for _ in range(1000):assert fn()==cookie
 print('Native x64 leaf-frame smoke passed: scratch loss reproduced unprotected; protected frame retained locals and returned correctly 1000 times.')
finally:k.VirtualFree(base,0,0x8000)
