import os
"""Repeatable process-only Here They Lie shared-image stereo diagnostic."""
import subprocess,sys
from pathlib import Path
root=Path(os.environ.get('HTL_TEST_ROOT', str(Path.home()/'Documents/Codex/HTL-Test')))
running=subprocess.check_output(['tasklist','/FI','IMAGENAME eq shadps4.exe','/FO','CSV','/NH'],text=True)
if 'shadps4.exe' in running.lower():
 print('Close the existing emulator before starting this test.');sys.exit(1)
command=root/'game/uroot/ue4commandline.txt'
original=command.read_bytes()
inputs=root/'tools/four-view-input.txt'
inputs.write_text('0 3600 head=0,0,1.5,0,0,0 worn=1\n65 1 recenter\n')
try:
 flags=[x for x in original.decode('utf-8-sig').split() if x.lower()!='-nohmd']
 if '-noasyncloadingthread' not in [x.lower() for x in flags]:flags.append('-NoAsyncLoadingThread')
 command.write_text(' '.join(flags)+'\n')
 subprocess.run([sys.executable,str(root/'tools/four-view-diagnostic.py'),'--adapt','--stationary','--gpu-compat'],check=True)
 print('VR diagnostic running. Recenter at 65 seconds. Start New Game, then use Apply-Here-They-Lie-Eye-Sampling.cmd after the subway loads.')
finally:
 command.write_bytes(original)
