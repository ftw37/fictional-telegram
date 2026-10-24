import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from launch_here_they_lie import validate_button_replay


class ButtonReplay(unittest.TestCase):
    def test_accepts_controller_route(self):
        validate_button_replay('# route\n0 7200\n94 3 options\n114 .3 cross\n232 .5 lx=128 ly=0 rx=255\n')

    def test_rejects_pose_and_tracking_overrides(self):
        for token in ('head=0,0,0,0,0,0', 'padrot=0,30,0', 'hands=off', 'worn=1', 'recenter'):
            with self.subTest(token=token), self.assertRaises(ValueError):
                validate_button_replay(f'0 1 {token}')

    def test_rejects_invalid_time_and_stick_values(self):
        for line in ('0', 'nan 1 cross', '0 -1 cross', '0 1 rx=256', '0 1 ly=-1', '0 1 rx=oops'):
            with self.subTest(line=line), self.assertRaises(ValueError):
                validate_button_replay(line)
