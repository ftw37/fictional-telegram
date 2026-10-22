"""Launch the tested flat-camera configuration without automatic game input."""
import os,subprocess
from pathlib import Path
root=Path(os.environ.get('HTL_TEST_ROOT', str(Path.home()/'Documents/Codex/HTL-Test')))
# Avoid accidentally opening a second emulator over the current session.
listing=subprocess.run(['tasklist','/FI','IMAGENAME eq shadps4.exe','/FO','CSV','/NH'],capture_output=True,text=True,creationflags=0x08000000)
if 'shadps4.exe' in listing.stdout.lower():
 print('The emulator is already running. Close it before launching another session.');raise SystemExit(1)
command_file=root/'game/uroot/ue4commandline.txt'
text=command_file.read_text() if command_file.exists() else ''
tokens=text.split()
for flag in ('-nohmd','-NoAsyncLoadingThread'):
 if flag.lower() not in [t.lower() for t in tokens]:tokens.append(flag)
command_file.write_text(' '.join(tokens)+'\n',encoding='ascii')
env=os.environ.copy()
for key in ('SHADPS4_INPUT_SCRIPT','SHADPS4_LIVE_INPUT'):
 env.pop(key,None)
env.update(SHADPS4_OPENXR='0',SHADPS4_XR_WAIT='0',SHADPS4_VR_DEMO='0',SHADPS4_VR_DESKTOP_VIEW='spectator')
log=open(root/'tools/flat-launch.log','w')
p=subprocess.Popen([str(root/'pc-vr/shadps4.exe'),'-g',str(root/'game/uroot/eboot.bin'),'--ignore-game-patch','--fullscreen','false'],cwd=root/'pc-vr',env=env,stdout=log,stderr=log)
(root/'tools/adapted-test-pid.txt').write_text(str(p.pid))
print('Flat-camera session started. No calibration or automatic button presses. Async package-loading thread disabled for the loading-crash test.')
