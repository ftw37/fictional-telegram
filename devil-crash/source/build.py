"""Rebuild Windows x64 release with Python 3.10+ and Zig on PATH.
Run: python source/build.py
Optional: --zig /path/to/zig --jobs 4
"""
import argparse,concurrent.futures,json,pathlib,shutil,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--zig',default='zig');p.add_argument('--jobs',type=int,default=4);a=p.parse_args()
root=pathlib.Path(__file__).resolve().parent;runtime=root/'runtime';out=root.parent
config=json.loads((root/'build-config.json').read_text());build=root/'build';build.mkdir(exist_ok=True)
zig=shutil.which(a.zig) or a.zig
version=subprocess.check_output([zig,'version'],text=True).strip();print('Zig',version,'(release built with',config['zig_version']+')')
subprocess.run([sys.executable,str(root/'recompile.py'),str(out/'game.md'),str(runtime)],check=True)
flags=['-target','x86_64-windows-gnu','-O2','-DNDEBUG']+['-D'+d for d in config['defines']]+['-I'+str(runtime/d) for d in config['includes']]
def compile_one(source):
 obj=build/(source.replace('/','_')+'.o')
 subprocess.run([zig,'cc',*flags,'-c',str(runtime/source),'-o',str(obj)],check=True)
 print(source,flush=True);return obj
with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,a.jobs)) as pool:objects=list(pool.map(compile_one,config['sources']))
subprocess.run([zig,'cc','-target','x86_64-windows-gnu','-shared',*[str(o) for o in objects],'-o',str(out/'devil-native.dll'),'-lm'],check=True)
subprocess.run([zig,'c++','-target','x86_64-windows-gnu','-std=c++17','-O2','-static','-Wl,--subsystem,windows',str(root/'player.cpp'),'-o',str(out/'DevilCrash.exe'),'-luser32','-lgdi32','-lwinmm','-lshell32','-lbcrypt'],check=True)
print('Built DevilCrash.exe and devil-native.dll')
