import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from render_profile_report import parse_log,aligned_stages

class ClockAlignment(unittest.TestCase):
    def test_frame_interval_report(self):
        windows,_=parse_log('frame stats at 10 s: 60 fps; unix 100; window 5; frames 300\n'
            'rendered frame intervals: p50 16.667 ms; p95 17.100 ms; p99 22.200 ms; '
            'max 48.000 ms; over20 7; over33 2; samples 300')
        self.assertEqual(windows[0]['intervals_ms']['p99'],22.2)
        self.assertEqual(windows[0]['interval_samples'],300)
        stage=aligned_stages([dict(event='start',unix_seconds=94),dict(event='end',unix_seconds=101)],windows)[0]
        self.assertEqual(stage['worst_window_p99_ms'],22.2)
        self.assertEqual(stage['intervals_over33'],2)

    def test_absolute_window_and_nested_scopes(self):
        text=('frame stats at 50 s: 11.0 fps, per frame 5500 passes, 5500 draws, GPU busy 45%; '
              'unix 100.000000; window 2.000000; frames 22\n'
              'CPU/driver scopes per frame (overlap; not additive): bind resources 5500x 12.50 ms, '
              'HTL dependency (inclusive) 5500x 20.00 ms\n'
              'frame path: (75.0 ms of its time per frame)')
        windows,_=parse_log(text)
        self.assertEqual(windows[0]['unix_start'],98)
        self.assertEqual(windows[0]['scopes_ms']['bind resources'],12.5)
        self.assertEqual(windows[0]['translation_cpu_ms'],75)
        stages=aligned_stages([dict(event='woman',unix_seconds=97),
                               dict(event='entry',unix_seconds=101)],windows)
        self.assertEqual(stages[0]['median_fps'],11)

    def test_profile_window_excluded(self):
        windows,_=parse_log('GPU_PROFILE_CLOCK frame=1 unix=99.1\n'
            'frame stats at 50 s: 11 fps; unix 100; window 2; frames 22')
        stages=aligned_stages([dict(event='start',unix_seconds=97),
                               dict(event='end',unix_seconds=101)],windows)
        self.assertEqual(stages[0]['clean_windows'],0)

    def test_partial_window_and_legacy_not_assigned(self):
        windows,_=parse_log('frame stats at 50 s: 60 fps\n'
            'frame stats at 52 s: 11 fps; unix 100; window 2; frames 22')
        stages=aligned_stages([dict(event='start',unix_seconds=99),
                               dict(event='end',unix_seconds=101)],windows)
        self.assertEqual(stages[0]['clean_windows'],0)

    def test_long_profile_spills_into_next_window(self):
        windows,_=parse_log('GPU_PROFILE_CLOCK frame=1 unix=97\n'
            'GPU_PROFILE_END sequence=1 unix=100.5\n'
            'frame stats at 50 s: 11 fps; unix 102; window 2; frames 22')
        self.assertTrue(windows[0]['profile_affected'])

    def test_gpu_frame_clock(self):
        _,profiles=parse_log('GPU_PROFILE_CLOCK frame=42 unix=100.25\n'
            'GPU profile 1 at 30 s: 5000 draws (200 thousand vertices) and 30 dispatches took '
            '80.00 ms timed one by one: 20.00 in themselves, 60.00 in what came between')
        self.assertEqual(profiles[0]['unix_seconds'],100.25)
        self.assertEqual(profiles[0]['between_work_ms'],60)

if __name__=='__main__':unittest.main()
