"""Launch the source-built HTL experiment without the old memory-address adapters.

Game data and the prepared runtime are local prerequisites, never distributed here.
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
from pathlib import Path
import subprocess
import time


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("preview", "quest", "flat"), default="preview")
    parser.add_argument("--development-root", type=Path,
                        default=Path.home() / "Documents/Codex/HTL-Development")
    parser.add_argument("--game", type=Path,
                        default=Path.home() / "Documents/Codex/HTL-Test/game/uroot")
    parser.add_argument("--replay", type=Path, help="Optional diagnostic input script")
    parser.add_argument("--tv-preview", action="store_true",
                        help="Open the optional TV preview window (off by default)")
    parser.add_argument("--frame-stats", action="store_true",
                        help="Collect lightweight frame timing for route comparisons")
    parser.add_argument("--profile-render", action="store_true",
                        help="Diagnostic CPU call timing and one GPU frame every 15 seconds")
    parser.add_argument("--profile-cpu", action="store_true",
                        help="CPU call timing with aligned FPS windows and no GPU timestamp capture")
    parser.add_argument("--fast-graphics", action="store_true",
                        help="Diagnostic graphics-state rebinding (reported visual glitches; not recommended)")
    args = parser.parse_args()
    root = args.development_root.resolve()
    runtime = root / "test-vr"
    exe = runtime / "shadps4.exe"
    game = args.game.resolve()
    if not exe.is_file() or not (game / "eboot.bin").is_file():
        raise RuntimeError("The prepared emulator or your extracted game is missing.")
    if args.mode == "quest" and args.replay:
        raise RuntimeError("Use preview mode for scripted poses; Quest mode uses the headset.")

    # A named mutex prevents two copies of this launcher changing the game flags at once.
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateMutexW.restype = ctypes.c_void_p
    kernel.CreateMutexW.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p)
    kernel.CloseHandle.argtypes = (ctypes.c_void_p,)
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.OpenProcess.argtypes = (ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32)
    kernel.WaitForSingleObject.argtypes = (ctypes.c_void_p, ctypes.c_uint32)
    kernel.QueryFullProcessImageNameW.argtypes = (
        ctypes.c_void_p, ctypes.c_uint32, ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_uint32))
    ctypes.set_last_error(0)
    mutex = kernel.CreateMutexW(None, False, "Local\\HereTheyLieSourceLauncher")
    if not mutex or ctypes.get_last_error() == 183:
        if mutex:
            kernel.CloseHandle(mutex)
        raise RuntimeError("The Here They Lie launcher is already running. Close its game first.")
    try:
        active_file = root / "active-run.json"
        if active_file.exists():
            active = json.loads(active_file.read_text(encoding="utf-8"))
            handle = kernel.OpenProcess(0x101000, False, int(active["pid"]))
            if handle:
                try:
                    name = ctypes.create_unicode_buffer(32768)
                    length = ctypes.c_uint32(len(name))
                    if (kernel.WaitForSingleObject(handle, 0) == 258 and
                            kernel.QueryFullProcessImageNameW(handle, 0, name, ctypes.byref(length)) and
                            Path(name.value).resolve() == exe.resolve()):
                        raise RuntimeError("The test emulator is already open. Close it before launching again.")
                finally:
                    kernel.CloseHandle(handle)
        env = os.environ.copy()
        for key in ("SHADPS4_INPUT_SCRIPT", "SHADPS4_LIVE_INPUT", "SHADPS4_VR_SOCKET",
                    "SHADPS4_HTL_TEST_UNCAP", "SHADPS4_HTL_SLEEP_TRACE",
                    "SHADPS4_HTL_TEST_VBLANK_HZ", "SHADPS4_HTL_NO_PRESENT", "SHADPS4_GPU_PROFILE",
                    "SHADPS4_FRAME_STATS", "SHADPS4_DBG_CALL_TIMES",
                    "SHADPS4_DBG_SKIP_PS", "SHADPS4_DBG_DRAW_VERTICES",
                    "SHADPS4_NGS2_TRACE", "SHADPS4_NGS2_DUMP", "SHADPS4_AUDIO3D_TRACE",
                    "SHADPS4_AUDIO3D_DUMP", "SHADPS4_HTL_AUDIO_TRACE"):
            env.pop(key, None)
        env.update(SHADPS4_HTL_COMPAT="1", SHADPS4_HTL_NATIVE_CLIP="1",
                   SHADPS4_HTL_TOUCH_CONTROLS="1",
                   SHADPS4_HTL_AUTO_CALIBRATE="1" if args.mode == "quest" else "0",
                   SHADPS4_HTL_THEATRE="1" if args.mode == "quest" else "0",
                   SHADPS4_HTL_XR_FLIP_Y="1" if args.mode == "quest" else "0",
                   SHADPS4_HTL_FRAME_SYNC="0", SHADPS4_HTL_DRAW_SYNC="0",
                   SHADPS4_HTL_GPU_BARRIER="1",
                   SHADPS4_HTL_BARRIER_MODE="pipeline" if args.fast_graphics else "broad",
                   SHADPS4_HTL_FX2="1", SHADPS4_HTL_AUDIO_DB="1",
                   SHADPS4_OPENXR="1" if args.mode == "quest" else "0",
                   SHADPS4_XR_WAIT="0", SHADPS4_VR_DEMO="0",
                   SHADPS4_VR_DESKTOP_GESTURES="1" if args.mode == "preview" else "0",
                   SHADPS4_VR_DESKTOP_VIEW="stereo", SHADPS4_DBG_EYE_SCAN="0",
                   SHADPS4_SHOT_SECONDS="0")
        if args.mode == "preview":
            if args.profile_cpu:
                env.update(SHADPS4_FRAME_STATS="1", SHADPS4_FRAME_STATS_EVERY="2",
                           SHADPS4_DBG_CALL_TIMES="1")
            if args.profile_render:
                env.update(SHADPS4_FRAME_STATS="1", SHADPS4_FRAME_STATS_EVERY="2",
                           SHADPS4_DBG_CALL_TIMES="1", SHADPS4_GPU_PROFILE="15")
            if args.frame_stats:
                env["SHADPS4_FRAME_STATS"] = "1"
                env["SHADPS4_FRAME_STATS_EVERY"] = "2" if args.profile_render or args.profile_cpu else "5"
            env["SHADPS4_HTL_THEATRE_PREVIEW"] = "1"
        else:
            env.pop("SHADPS4_HTL_THEATRE_PREVIEW", None)
        if args.tv_preview and args.mode != "flat":
            env["SHADPS4_SOCIAL_PREVIEW"] = "1"
        else:
            env.pop("SHADPS4_SOCIAL_PREVIEW", None)
        if args.replay:
            env["SHADPS4_INPUT_SCRIPT"] = str(args.replay.resolve(strict=True))
            env["SHADPS4_LIVE_INPUT"] = str(args.replay.resolve(strict=True))

        commandline = game / "ue4commandline.txt"
        old_flags = commandline.read_bytes() if commandline.exists() else None
        flags = b"-nohmd -NoAsyncLoadingThread\n" if args.mode == "flat" else b"-NoAsyncLoadingThread\n"
        recovery = root / "launcher-commandline-recovery.json"
        recovery.write_text(json.dumps({"path": str(commandline),
                                       "previous_hex": old_flags.hex() if old_flags is not None else None}),
                            encoding="utf-8")
        commandline.write_bytes(flags)
        try:
            with (root / "source-launcher-stdout.log").open("w", encoding="utf-8") as log:
                process = subprocess.Popen(
                    [str(exe), "-g", str(game / "eboot.bin"), "--ignore-game-patch",
                     "--fullscreen", "false", "--show-fps"], cwd=runtime, env=env, stdout=log, stderr=log,
                    creationflags=subprocess.CREATE_NO_WINDOW)
                (root / "active-run.json").write_text(json.dumps({
                    "pid": process.pid, "started": time.time(), "exe": str(exe), "mode": args.mode}),
                    encoding="utf-8")
                return process.wait()
        finally:
            # Preserve a user's later edit rather than silently replacing it.
            if commandline.exists() and commandline.read_bytes() == flags:
                if old_flags is None:
                    commandline.unlink()
                else:
                    commandline.write_bytes(old_flags)
    finally:
        kernel.CloseHandle(mutex)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        error_path = Path.home() / "Documents/Codex/HTL-Development/launcher-error.txt"
        error_path.parent.mkdir(parents=True, exist_ok=True)
        error_path.write_text(str(error), encoding="utf-8")
        raise
