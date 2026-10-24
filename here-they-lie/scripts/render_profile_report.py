"""Align profiling windows with route events using shared Unix timestamps.

Keep generated reports local: source logs include shader hashes and guest addresses.
"""
import argparse
import json
from pathlib import Path
import re
import statistics

def parse_log(text):
    windows=[]
    profiles=[]
    clocks=[]
    ends={}
    current=None
    for line in text.splitlines():
        clock=re.search(r'GPU_PROFILE_CLOCK frame=(\d+) unix=([\d.]+)',line)
        if clock:clocks.append(float(clock[2]))
        end=re.search(r'GPU_PROFILE_END sequence=(\d+) unix=([\d.]+)',line)
        if end:ends[int(end[1])]=float(end[2])
        match=re.search(r'frame stats at ([\d.]+) s.*?: ([\d.]+) fps',line)
        if match:
            current=dict(frame_stats_seconds=float(match[1]),fps=float(match[2]),scopes_ms={})
            for name,pattern in [('draws',r'([\d.]+) draws'),('passes',r'([\d.]+) passes'),
                                 ('gpu_busy_percent',r'GPU busy ([\d.]+)%')]:
                value=re.search(pattern,line)
                if value:current[name]=float(value[1])
            stamp=re.search(r'; unix ([\d.]+); window ([\d.]+); frames (\d+)',line)
            if stamp:
                current.update(unix_end=float(stamp[1]),window_seconds=float(stamp[2]),frames=int(stamp[3]))
                current['unix_start']=current['unix_end']-current['window_seconds']
            windows.append(current)
        if current is not None:
            if 'CPU/driver scopes per frame' in line or 'driver calls per frame' in line:
                for name,count,ms in re.findall(r'([^:,]+?) ([\d.]+)x ([\d.]+) ms',line):
                    current['scopes_ms'][name.strip()]=float(ms)
            cpu=re.search(r'\(([\d.]+) ms of its time per frame\)',line)
            if cpu:current['translation_cpu_ms']=float(cpu[1])
        profile=re.search(r'GPU profile (\d+).*?: (\d+) draws .*? and (\d+) dispatches took '
                          r'([\d.]+) ms timed one by one: ([\d.]+) in themselves, ([\d.]+) in what came between',line)
        if profile:
            seq=int(profile[1])
            profiles.append(dict(sequence=seq,unix_seconds=clocks[seq-1] if seq<=len(clocks) else None,
                draws=int(profile[2]),dispatches=int(profile[3]),serialized_span_ms=float(profile[4]),
                draw_dispatch_ms=float(profile[5]),between_work_ms=float(profile[6])))
    for window in windows:
        window['profile_affected']=any(at<=window.get('unix_end',float('-inf'))+.5 and
            ends.get(i+1,at)+.5>=window.get('unix_start',float('inf'))
            for i,at in enumerate(clocks))
    return windows,profiles

def aligned_stages(events,windows):
    events=sorted((e for e in events if 'unix_seconds' in e),key=lambda e:e['unix_seconds'])
    stages=[]
    for start,end in zip(events,events[1:]):
        lo,hi=start['unix_seconds'],end['unix_seconds']
        if 'sample_duration_seconds' in start:
            hi=min(hi,lo+start['sample_duration_seconds'])
        samples=[w for w in windows if 'unix_start' in w and lo<=w['unix_start'] and w['unix_end']<=hi
                 and not w['profile_affected']]
        def median(key):
            vals=[w[key] for w in samples if key in w]
            return round(statistics.median(vals),3) if vals else None
        scope_names=set().union(*(w['scopes_ms'] for w in samples)) if samples else set()
        stages.append(dict(stage=start['event'],seconds=round(hi-lo,3),clean_windows=len(samples),
            median_fps=median('fps'),median_draws=median('draws'),
            median_translation_cpu_ms=median('translation_cpu_ms'),
            scopes_median_ms={name:round(statistics.median(w['scopes_ms'][name]
                for w in samples if name in w['scopes_ms']),3) for name in sorted(scope_names)}))
    return stages

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path)
    args=parser.parse_args()
    windows,profiles=parse_log((args.run/'shad_log.txt').read_text(errors='replace'))
    events=[json.loads(line) for line in (args.run/'events.jsonl').read_text().splitlines()]
    extra=args.run/'scene-markers.jsonl'
    if extra.exists():events += [json.loads(line) for line in extra.read_text().splitlines()]
    result=dict(note='CPU scopes overlap and must not be summed. GPU timestamps serialize one frame; '
                     'profile-affected FPS windows are excluded. Neither is an ordinary frame-time percentile.',
                stages=aligned_stages(events,windows),windows=windows,gpu_profiles=profiles)
    (args.run/'render-profile.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(dict(stages=result['stages'],gpu_profiles=profiles),indent=2))

if __name__=='__main__':main()
