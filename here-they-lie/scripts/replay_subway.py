"""Local CUSA05344 01.00 route: New Game to platform. Resets game progress."""
import argparse, hashlib, json, math
from pathlib import Path
import shutil, subprocess, sys, time
from subway_position import PositionReader

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reset-progress',action='store_true',required=True)
    p.add_argument('--label',default=time.strftime('subway-%Y%m%d-%H%M%S'))
    p.add_argument('--profile-render',action='store_true')
    p.add_argument('--profile-cpu',action='store_true')
    p.add_argument('--compare-image-lookup',action='store_true')
    p.add_argument('--compare-clean-upload',action='store_true',
                   help='Diagnostic off/on/off comparison before traversal, then candidate route')
    a=p.parse_args()
    if not a.label.replace('-','').replace('_','').isalnum(): p.error('Use a plain label')
    root=Path.home()/'Documents/Codex/HTL-Development'
    if a.compare_clean_upload and a.compare_image_lookup:
        p.error('Compare one candidate at a time')
    comparing=a.compare_clean_upload or a.compare_image_lookup
    experiment='image_lookup' if a.compare_image_lookup else 'clean_upload'
    hold_seconds=6 if a.compare_image_lookup else 12
    fastpath_flag=root/('test-vr/user/htl-exact-image-lookup' if a.compare_image_lookup
                       else 'test-vr/user/htl-clean-upload-fastpath')
    if comparing and fastpath_flag.exists():
        raise RuntimeError(f'Remove the existing diagnostic override first: {fastpath_flag}')
    out=root/'performance-runs'/a.label
    out.mkdir(parents=True,exist_ok=False)
    script=out/'inputs.txt'
    script.write_text('0 7200 head=0,0,0,0,0,0 worn=1\n50 2 options\n70 0.1 down\n84 0.3 cross\n110 0.3 cross\n')
    process=subprocess.Popen([sys.executable,str(Path(__file__).with_name('launch_here_they_lie.py')),
        '--mode','preview','--game',str(Path.home()/'Documents/Codex/HTL-Test/no-vignette-v1/uroot'),
        '--replay',str(script),'--frame-stats']+(['--profile-render'] if a.profile_render else [])
        +(['--profile-cpu'] if a.profile_cpu else []))
    reader=None
    owns_fastpath_flag=False
    active=None
    begun=time.monotonic()
    events=[]
    def event(name,**kw):
        item=dict(event=name,wall_seconds=round(time.monotonic()-begun,3),**kw)
        if active:
            item['emulator_seconds']=round(time.time()-active['started'],3)
        item['unix_seconds']=time.time()
        events.append(item)
        with (out/'events.jsonl').open('a') as f:f.write(json.dumps(item)+'\n')
        print(json.dumps(item),flush=True)
    try:
        deadline=time.monotonic()+30
        active=None
        while time.monotonic()<deadline:
            if process.poll() is not None:raise RuntimeError('Launcher exited')
            try:
                candidate=json.loads((root/'active-run.json').read_text())
                if candidate['started']>time.time()-30:active=candidate;break
            except (OSError,ValueError):pass
            time.sleep(.2)
        if active is None:raise RuntimeError('No fresh emulator run')
        event('startup_wait',until_emulator_seconds=195)
        exe=Path(active['exe'])
        (out/'metadata.json').write_text(json.dumps(dict(
            emulator_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),
            game='CUSA05344 01.00',route_version=2,barrier='broad',smooth_turning_required=True,
            runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            profile_render=a.profile_render, compare_clean_upload=a.compare_clean_upload,
            profile_cpu=a.profile_cpu, compare_image_lookup=a.compare_image_lookup,
            launch_unix_seconds=active['started']),indent=2))
        def sample():return reader.sample()
        def pulse(seconds,tokens):
            if process.poll() is not None:raise RuntimeError('Emulator exited')
            start=time.time()-active['started']+.15
            with script.open('a') as f:f.write(f'{start:.3f} {seconds:.3f} {tokens}\n')
            time.sleep(seconds+.35)
            return sample()
        while time.time()-active['started']<195:
            if process.poll() is not None:raise RuntimeError('Emulator exited during startup')
            time.sleep(.2)
        reader=PositionReader(active['pid'],exe)
        for attempt in range(4):
            try:state=reader.discover();break
            except RuntimeError:
                if attempt==3:raise
                time.sleep(10)
        if not (600<state['local'][0]<1000 and abs(state['local'][1])<150
                and 60<state['local'][2]<110):
            raise RuntimeError('Startup did not reach the expected first-car spawn')
        if comparing:
            event(experiment+'_baseline_start',position=sample(),sample_duration_seconds=hold_seconds)
            time.sleep(hold_seconds)
            fastpath_flag.touch();owns_fastpath_flag=True
            time.sleep(1.5)
            event(experiment+'_candidate_start',position=sample(),sample_duration_seconds=hold_seconds)
            time.sleep(hold_seconds)
            fastpath_flag.unlink();time.sleep(1.5)
            event(experiment+'_restored_start',position=sample(),sample_duration_seconds=hold_seconds)
            time.sleep(hold_seconds)
            fastpath_flag.touch();time.sleep(1.5)
        event('route_start',position=sample())
        def align(target=0):
            for _ in range(35):
                state=sample();error=(target-state['yaw']+180)%360-180
                if abs(error)<1.5:return state
                duration=min(.5,max(.12,abs(error)/45))
                axis=(180 if error>0 else 75) if abs(error)<8 else (255 if error>0 else 0)
                pulse(duration,f'rx={axis}')
            raise RuntimeError('Cannot align: confirm smooth turning')
        def center():
            align()
            for _ in range(25):
                state=sample();y=state['local'][1]
                if abs(y)<12:return state
                pulse(min(.7,max(.15,(abs(y)-5)/38)),f'lx={0 if y>0 else 255}')
            raise RuntimeError('Cannot center aisle')
        def drive(target=55,timeout=100,transition=False,scare_marker=False):
            state=center();base=state['base'];end=time.monotonic()+timeout
            marked_region=False;marked_pause=False;last_x=None
            while time.monotonic()<end:
                state=sample()
                if scare_marker and 850<state['local'][0]<1100:
                    if not marked_region:
                        event('scare_region_entered',position=state);marked_region=True
                    if last_x is not None and abs(state['local'][0]-last_x)<5 and not marked_pause:
                        event('scare_movement_pause',position=state);marked_pause=True
                if state['base']!=base:
                    if transition:return state
                    raise RuntimeError('Unexpected car transition')
                delta=state['local'][0]-target
                if not transition and (abs(delta)<30 or (target<100 and state['local'][0]<80)):
                    return state
                if abs(state['local'][1])>25 or abs(state['yaw'])>2:center()
                near=abs(delta)<180
                last_x=state['local'][0]
                pulse(.25 if near else .7,
                      f'ly={0 if delta>0 or transition else 255}'+('' if near else ' r2'))
            raise RuntimeError('Aisle timeout: stop or obstruction did not clear')
        for car in range(1,4):
            event(f'car_{car}_start',position=sample())
            event(f'car_{car}_end_door',position=drive(scare_marker=car==2))
            pulse(.4,'cross');time.sleep(1)
            old=sample()['base'];deadline=time.monotonic()+20
            while sample()['base']==old and time.monotonic()<deadline:pulse(.5,'ly=0')
            if sample()['base']==old:raise RuntimeError('Connection blocked')
            # The movement base can change before the next door is within reach.
            # Approach the closed door rather than pressing Cross immediately.
            approach_deadline=time.monotonic()+12
            while (sample()['base']==old or sample()['local'][0]>1590) and time.monotonic()<approach_deadline:
                pulse(.3,'ly=0')
            if sample()['base']==old or sample()['local'][0]>1610:
                raise RuntimeError('Cannot approach next entrance door')
            event(f'car_{car+1}_entrance',position=sample())
            pulse(.4,'cross');time.sleep(1.5)
        event('fire_car_start',position=sample())
        state=drive(timeout=120,transition=True)
        if state['world'][2]<2500:raise RuntimeError('Expected station transition')
        event('station_car',position=state)
        drive(target=780,timeout=50)
        align(-90)
        old=sample()['base'];deadline=time.monotonic()+20
        while sample()['base']==old and time.monotonic()<deadline:pulse(.3,'ly=0')
        if sample()['base']==old:raise RuntimeError('Platform doorway blocked')
        pulse(.5,'ly=0')
        event('platform_reached',position=sample())
        (out/'result.json').write_text(json.dumps(dict(status='platform_reached',
            elapsed_seconds=events[-1]['wall_seconds']-next(e['wall_seconds'] for e in events if e['event']=='route_start'),
            note='Waypoint result; visually verify platform endpoint.'),indent=2))
    except Exception as error:
        event('failed',reason=str(error))
        (out/'result.json').write_text(json.dumps(dict(status='failed',reason=str(error)),indent=2))
        raise
    finally:
        # Finite pulses expire on failure; leave the game open for inspection.
        if reader:reader.close()
        if owns_fastpath_flag and fastpath_flag.exists():fastpath_flag.unlink()
        for source in (root/'test-vr/user/log/shad_log.txt',root/'source-launcher-stdout.log'):
            if source.exists():shutil.copy2(source,out/source.name)
    print(f'Run saved to {out}. Game remains open.',flush=True)

if __name__=='__main__':main()
