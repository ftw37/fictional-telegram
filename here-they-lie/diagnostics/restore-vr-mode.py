import os
from pathlib import Path
p=Path(os.environ.get('HTL_TEST_ROOT', str(Path.home()/'Documents/Codex/HTL-Test')))/'game/uroot/ue4commandline.txt'
s=p.read_text() if p.exists() else ''
tokens=s.split();tokens=[t for t in tokens if t.lower() not in ('-nohmd','-noasyncloadingthread')]
p.write_text((' '.join(tokens)+'\n') if tokens else '',encoding='ascii')
print('Removed the flat-camera flag. The regular VR test launchers can be used again.')
