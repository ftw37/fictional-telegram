"""Summarize five-second frame-stat windows within replay route stages."""
import argparse, json, re
from pathlib import Path

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path)
    parser.add_argument('--clock-offset-seconds',type=float,
                        help='Measured launcher time minus frame-stat clock time; omit if unknown')
    args=parser.parse_args()
    events=[json.loads(line) for line in (args.run/'events.jsonl').read_text().splitlines()]
    stats=[(float(t),float(fps)) for t,fps in re.findall(
        r'frame stats at ([\d.]+) s: ([\d.]+) fps',
        (args.run/'shad_log.txt').read_text(errors='replace'))]
    result={'note':'FPS values are five-second window averages. Without a calibrated clock offset they are not assigned to route stages.',
            'fps_windows':[dict(frame_stats_seconds=t,fps=fps) for t,fps in stats],
            'stages':[]}
    for start,end in zip(events,events[1:]):
        if 'emulator_seconds' not in start or 'emulator_seconds' not in end:continue
        low,high=start['emulator_seconds'],end['emulator_seconds']
        # Only complete windows within a stage; avoid mixing door/scare transitions.
        samples=[] if args.clock_offset_seconds is None else [fps for at,fps in stats
            if low+5<=at+args.clock_offset_seconds<=high]
        result['stages'].append(dict(stage=start['event'],seconds=round(high-low,3),
            windows=len(samples),mean_window_fps=round(sum(samples)/len(samples),2) if samples else None,
            lowest_window_fps=min(samples) if samples else None))
    (args.run/'summary.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
