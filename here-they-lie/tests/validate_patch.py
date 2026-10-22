"""Verify that the compatibility patch applies to pristine files from its Git revision."""
import argparse
import hashlib
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source", type=Path, required=True)
parser.add_argument("--patch", type=Path, required=True)
parser.add_argument("--git", default="git")
parser.add_argument("--scratch", type=Path, required=True)
parser.add_argument("--compare-working-tree", action="store_true")
args = parser.parse_args()
patch = args.patch.resolve()
data = patch.read_bytes()
paths = re.findall(r"^\+\+\+ b/(.+)$", data.decode("utf-8"), re.MULTILINE)
args.scratch.mkdir(parents=True, exist_ok=True)
scratch = Path(tempfile.mkdtemp(prefix="htl-patch-", dir=args.scratch))
for name in paths:
    parts = PurePosixPath(name)
    if parts.is_absolute() or ".." in parts.parts or not name.startswith("shadps4-arm64-main/"):
        raise ValueError(f"Unexpected patch path: {name}")
    original = subprocess.run([args.git, "-C", str(args.source), "show", f"HEAD:{name}"],
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if original.returncode == 0:
        target = scratch / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(original.stdout)
subprocess.run([args.git, "init", "--quiet", str(scratch)], check=True)
subprocess.run([args.git, "-C", str(scratch), "-c", "core.autocrlf=false", "apply", "--check", str(patch)], check=True)
subprocess.run([args.git, "-C", str(scratch), "-c", "core.autocrlf=false", "apply", str(patch)], check=True)
if args.compare_working_tree:
    for name in paths:
        expected = (args.source / name).read_bytes().replace(b"\r\n", b"\n")
        actual = (scratch / name).read_bytes().replace(b"\r\n", b"\n")
        if actual != expected:
            raise AssertionError(f"Round-trip differs: {name}")
print(f"PASS: patch applied to {len(paths)} pristine source files; SHA256 {hashlib.sha256(data).hexdigest()}")
