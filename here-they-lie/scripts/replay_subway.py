"""Local CUSA05344 01.00 route: New Game to platform. Resets game progress."""
import argparse, hashlib, json, math
from pathlib import Path
import shutil, subprocess, sys, time
from subway_position import PositionReader

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reset-progress',action='store_true',required=True)
    p.add_argument('--label',default=time.strftime('subway-%Y%m%d-%H%M%S'))
    a=p.parse_args()
    if not a.label.replace('-','').replace('_','').isalnum(): p.error('Use a plain label')
    root=Path.home()/'Documents/Codex/HTL-Development'
    out=root/'performance-runs'/a.label
    out.mkdir(parents=True,exist_ok=False)
    script=out/'inputs.txt'
    script.write_text('0 7200 head=0,0,0,0,0,0 worn=1\n50 2 options\n70 0.1 down\n84 0.3 cross\n110 0.3 cross\n')
    process=subprocess.Popen([sys.executable,str(Path(__file__).with_name('launch_here_they_lie.py')),
        '--mode','preview','--game',str(Path.home()/'Documents/Codex/HTL-Test/no-vignette-v1/uroot'),
        '--replay',str(script),'--frame-stats'])
    reader=None
    active=None
    begun=time.monotonic()
    events=[]
    def event(name,**kw):
        item=dict(event=name,wall_seconds=round(time.monotonic()-begun,3),**kw)
        if active:
            item['emulator_seconds']=round(time.time()-active['started'],3)
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
            game='CUSA05344 01.00',route_version=1,barrier='broad',smooth_turning_required=True),indent=2))
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
        event('route_start',position=state)
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
        def drive(target=55,timeout=100,transition=False):
            state=center();base=state['base'];end=time.monotonic()+timeout
            while time.monotonic()<end:
                state=sample()
                if state['base']!=base:
                    if transition:return state
                    raise RuntimeError('Unexpected car transition')
                delta=state['local'][0]-target
                if not transition and (abs(delta)<30 or (target<100 and state['local'][0]<80)):
                    return state
                if abs(state['local'][1])>25 or abs(state['yaw'])>2:center()
                near=abs(delta)<180
                pulse(.25 if near else .7,
                      f'ly={0 if delta>0 or transition else 255}'+('' if near else ' r2'))
            raise RuntimeError('Aisle timeout: stop or obstruction did not clear')
        for car in range(1,4):
            event(f'car_{car}_start',position=sample())
            event(f'car_{car}_end_door',position=drive())
            pulse(.4,'cross');time.sleep(1)
            old=sample()['base'];deadline=time.monotonic()+20
            while sample()['base']==old and time.monotonic()<deadline:pulse(.5,'ly=0')
            if sample()['base']==old:raise RuntimeError('Connection blocked')
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
        for source in (root/'test-vr/user/log/shad_log.txt',root/'source-launcher-stdout.log'):
            if source.exists():shutil.copy2(source,out/source.name)
    print(f'Run saved to {out}. Game remains open.',flush=True)

if __name__=='__main__':main()
