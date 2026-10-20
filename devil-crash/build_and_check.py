"""Stream a build and self-test to the console and build-log.txt."""
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
os.chdir(root)
with open('build-log.txt', 'w', encoding='utf-8') as log:
    def run(command):
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, errors='replace') as process:
            for line in process.stdout:
                print(line, end='', flush=True)
                log.write(line)
                log.flush()
            return process.wait()

    result = run([sys.executable, '-u', 'source/build.py', '--zig',
                  os.environ.get('DEVIL_ZIG', 'zig'), '--jobs', '2'])
    if result:
        print('Build failed. See build-log.txt.')
        sys.exit(result)
    result = run([str(root / 'DevilCrash.exe'), '--selftest=1800'])
    report = root / 'selftest.txt'
    if result == 0 and report.exists():
        text = report.read_text()
        print(text)
        log.write(text)
    sys.exit(result)
