"""Read-only route telemetry for the local CUSA05344 01.00 executable.

No process writes, controller injection, game assets, or raw memory dumps.
The offsets are game-version-specific and deliberately fail closed.
"""
import ctypes as C
from ctypes import wintypes as W
import math
from pathlib import Path
import re
import struct

class Region(C.Structure):
    _fields_ = [('address', C.c_void_p), ('allocation', C.c_void_p),
                ('allocation_protect', W.DWORD), ('partition', W.WORD),
                ('size', C.c_size_t), ('state', W.DWORD),
                ('protect', W.DWORD), ('type', W.DWORD)]

class PositionReader:
    def __init__(self, pid, executable, image_base=0x800000000):
        self.k = C.WinDLL('kernel32', use_last_error=True)
        self.k.OpenProcess.argtypes = [W.DWORD, W.BOOL, W.DWORD]
        self.k.OpenProcess.restype = W.HANDLE
        self.k.ReadProcessMemory.argtypes = [W.HANDLE, C.c_void_p, C.c_void_p,
                                            C.c_size_t, C.POINTER(C.c_size_t)]
        self.k.VirtualQueryEx.argtypes = [W.HANDLE, C.c_void_p, C.POINTER(Region), C.c_size_t]
        self.k.VirtualQueryEx.restype = C.c_size_t
        self.k.QueryFullProcessImageNameW.argtypes = [W.HANDLE, W.DWORD, W.LPWSTR,
                                                     C.POINTER(W.DWORD)]
        self.k.CloseHandle.argtypes = [W.HANDLE]
        self.handle = self.k.OpenProcess(0x410, False, pid)
        if not self.handle:
            raise RuntimeError('Cannot open emulator for read-only route telemetry')
        name = C.create_unicode_buffer(32768)
        length = W.DWORD(len(name))
        if not self.k.QueryFullProcessImageNameW(self.handle, 0, name, C.byref(length)) or \
                Path(name.value).resolve() != Path(executable).resolve():
            self.close()
            raise RuntimeError('Emulator identity mismatch')
        self.player = None
        self.image_base = image_base

    def close(self):
        if self.handle:
            self.k.CloseHandle(self.handle)
            self.handle = None

    def read(self, address, length):
        data = C.create_string_buffer(length)
        done = C.c_size_t()
        if not self.k.ReadProcessMemory(self.handle, address, data, length, C.byref(done)):
            return b''
        return data.raw[:done.value]

    def ptr(self, address):
        data = self.read(address, 8)
        return struct.unpack('<Q', data)[0] if len(data) == 8 else 0

    def find_references(self, pointer):
        needle = struct.pack('<Q', pointer)
        address = 0x200000000
        while address < 0x300000000:
            region = Region()
            if not self.k.VirtualQueryEx(self.handle, address, C.byref(region), C.sizeof(region)):
                break
            first = region.address or address
            end = first + region.size
            if region.state == 0x1000 and region.protect in (4, 0x40):
                for at in range(max(address, first), min(end, 0x300000000), 8*1024*1024):
                    data = self.read(at, min(8*1024*1024, end-at))
                    for hit in re.finditer(re.escape(needle), data):
                        yield at + hit.start()
            if end <= address:
                break
            address = end

    def discover(self):
        native = self.ptr(self.image_base + 0x42c4ae0)
        if not native:
            raise RuntimeError('Player class unavailable; game build or startup state differs')
        meta = self.ptr(native + 0x10)
        classes = []
        for reference in self.find_references(native):
            obj = reference - 0x30
            parent = self.ptr(obj + 0x10)
            for _ in range(12):
                if parent == meta:
                    classes.append(obj)
                    break
                parent = self.ptr(parent + 0x30)
                if not parent:
                    break
        players = []
        for cls in classes:
            for reference in self.find_references(cls):
                obj = reference - 0x10
                if self.read(obj + 8, 4) == struct.pack('<I', 0x48) and \
                        self.image_base+0x3000000 < self.ptr(obj) < self.image_base+0x5000000:
                    players.append(obj)
        if len(set(players)) != 1:
            raise RuntimeError('Expected exactly one live player; wait for subway entry')
        self.player = players[0]
        return self.sample()

    @staticmethod
    def yaw(q):
        x,y,z,w = q
        return math.degrees(math.atan2(2*(w*z+x*y), 1-2*(y*y+z*z)))

    def sample(self):
        if self.player is None:
            raise RuntimeError('Player not discovered')
        root = self.ptr(self.player + 0x160)
        base = self.ptr(self.player + 0x3f8)
        transform = self.read(base + 0x110, 48)
        location = self.read(root + 0x120, 12)
        rotation = self.read(root + 0x110, 16)
        if len(transform) != 48 or len(location) != 12 or len(rotation) != 16:
            raise RuntimeError('Player transform unavailable')
        t = struct.unpack('<12f', transform)
        xyz = struct.unpack('<3f', location)
        q = struct.unpack('<4f', rotation)
        qx,qy,qz,qw = -t[0],-t[1],-t[2],t[3]
        vx,vy,vz = (xyz[i]-t[4+i] for i in range(3))
        tx,ty,tz = 2*(qy*vz-qz*vy),2*(qz*vx-qx*vz),2*(qx*vy-qy*vx)
        local = [(vx+qw*tx+qy*tz-qz*ty)/t[8],
                 (vy+qw*ty+qz*tx-qx*tz)/t[9],
                 (vz+qw*tz+qx*ty-qy*tx)/t[10]]
        heading = (self.yaw(q)-self.yaw(t[:4])+180)%360-180
        if not all(math.isfinite(v) for v in local+[heading]) or max(map(abs,local)) > 100000:
            raise RuntimeError('Invalid route transform; stopping controls')
        return dict(base=base, local=local, yaw=heading, world=list(xyz))
