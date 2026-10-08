"""Compile and compare the port against the recovered 6502 code.

Requires py65, Inform 7/6, and a Glulx interpreter. Diagnostic code is added to
a separate temporary project only; it is not present in the delivered story.
"""
import json
import argparse
import re
import subprocess
from pathlib import Path
from c64_reference import OriginalGame
from recover import generate

HERE = Path(__file__).parent
INFORM = Path('/workspace/inform-tools/usr/lib/x86_64-linux-gnu/inform7-ide')
INTERNAL = Path('/workspace/inform-tools/usr/share/inform7-ide')
GLULXE = '/workspace/glulxe/glulxe'


def compile_project(project, target):
    (project / 'Build').mkdir(exist_ok=True, parents=True)
    for cmd in [
        [str(INFORM / 'inform7'), '-internal', str(INTERNAL), '-project', str(project), '-release', '-no-index', '-no-progress'],
        [str(INFORM / 'inform6'), '-G', '-w', str(project / 'Build/auto.inf'), str(target)],
    ]:
        result = subprocess.run(cmd, text=True, capture_output=True)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)


def run_story(target, commands):
    result = subprocess.run([GLULXE, str(target)], input='\n'.join(commands) + '\n',
                            text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'Run-time problem' not in result.stdout, result.stdout
    return result.stdout


def main():
    data = json.loads((HERE / 'recovered-data.json').read_text())
    generate(data)
    source = (HERE / 'Inca Curse.ni').read_text()
    project = HERE / 'Inca Curse.inform'
    (project / 'Source').mkdir(parents=True, exist_ok=True)
    (project / 'Source/story.ni').write_text(source)
    compile_project(project, HERE / 'Inca Curse.ulx')

    diagnostic = HERE / 'build/Diagnostic.inform'
    (diagnostic / 'Source').mkdir(parents=True, exist_ok=True)
    source = source.replace('\tif adventure finished is true:', '\tdump recovered state;\n\tif adventure finished is true:')
    source += '''

To dump recovered state:
	say "PORTSTATE [current site]|[score]|";
	repeat with N running from 0 to 29:
		say "[register N],";
	say "|";
	repeat with N running from 0 to 47:
		say "[whereabouts of N],";
	say "|";
	if adventure finished is true:
		say "1";
	otherwise:
		say "0";
	say line break.
'''
    (diagnostic / 'Source/story.ni').write_text(source)
    target = HERE / 'build/diagnostic.ulx'
    compile_project(diagnostic, target)

    walkthrough = (HERE / 'walkthrough.txt').read_text().splitlines()
    opening = walkthrough[:8]
    fire_route = walkthrough[:32]
    sand_route = walkthrough[:8] + ['e', 'e', 'e', 's', 'w', 's', 'd', 'w', 'd']
    cases = {
        'treasure and escape': walkthrough,
        'failed commands and parser': ['xyz', 'take bran', 'cut bran', 'i', 'n', 'help', 'look bran', 'cut leav', 'take bran', 'take bran', 'drop bran', 'drop bran'],
        'fire death': fire_route + ['help'] * 9,
        'sand countdown': sand_route + ['help'] * 9,
        'carrying limit': opening + ['e', 'e', 'take blan', 'e', 'take key', 's', 'take matc', 'w', 'take chis', 's', 'take rope', 'i'],
    }
    count = 0
    report = []
    for label, commands in cases.items():
        game = OriginalGame()
        expected = []
        executed = []
        for command in commands:
            game.command(command)
            expected.append(game.state())
            executed.append(command)
            if game.ended:
                break
        transcript = run_story(target, executed + (['quit', 'y'] if not game.ended else ['quit']))
        (HERE / 'build' / (label.replace(' ', '-') + '.txt')).write_text(transcript)
        matches = re.findall(r'PORTSTATE (\d+)\|(\d+)\|([\d,]+)\|([\d,]+)\|([01])', transcript)
        assert len(matches) == len(expected), (label, len(matches), len(expected), transcript[-1000:])
        for command, state, match in zip(executed, expected, matches):
            site, score, registers, places, ended = match
            actual = dict(site=int(site), score=int(score),
                          registers=[int(x) for x in registers.split(',') if x],
                          places=[int(x) for x in places.split(',') if x], ended=ended == '1')
            assert actual == state, (label, command, actual, state)
        if label == 'treasure and escape':
            assert game.ended and expected[-1]['score'] == 200
            assert 'CONGRATULATIONS' in transcript
        if label == 'fire death':
            # The original fire rule incorrectly reuses the sand-death text.
            assert game.ended and 'SUFFOCATED' in transcript
        if label == 'sand countdown':
            # The uploaded build checks room 26 for this death, although the
            # dungeon is room 25. Its timer expires without killing the player.
            assert not game.ended and expected[-1]['site'] == 25
            assert expected[-1]['registers'][5] == 0
        count += len(expected)
        report.append(f'{label}: {len(expected)} commands; every room, score, register and object state matched the 6502 reference')
    plain = run_story(HERE / 'Inca Curse.ulx', walkthrough + ['quit'])
    assert 'CONGRATULATIONS' in plain and 'YOU HAVE A SCORE OF 200' in plain
    (HERE / 'build/winning-transcript.txt').write_text(plain)
    report.append(f'{count} differential command checks passed. Release story also completed the winning route.')

    saved_game = HERE / 'build/validation.glksave'
    if saved_game.exists():
        saved_game.unlink()
    restored = run_story(target, ['cut leav', 'take bran', 'save', str(saved_game),
                                  's', 'drop bran', 'restore', str(saved_game), 'i', 'r', 'quit', 'y'])
    restored_states = re.findall(r'PORTSTATE (\d+)\|(\d+)\|([\d,]+)\|([\d,]+)\|([01])', restored)
    assert len(restored_states) == 6, restored
    assert restored_states[1] == restored_states[4] == restored_states[5], restored_states
    assert saved_game.exists() and saved_game.stat().st_size > 0
    (HERE / 'build/save-restore-transcript.txt').write_text(restored)
    undone = run_story(target, ['cut leav', 'take bran', 's', 'undo', 'r', 'i', 'quit', 'y'])
    undo_states = re.findall(r'PORTSTATE (\d+)\|(\d+)\|([\d,]+)\|([\d,]+)\|([01])', undone)
    assert len(undo_states) == 5 and undo_states[1] == undo_states[3] == undo_states[4], undone
    assert 'Previous turn undone' in undone
    (HERE / 'build/undo-transcript.txt').write_text(undone)
    report.append('Inform SAVE/RESTORE and UNDO: location, inventory, registers and score restored correctly.')
    (HERE / 'validation.txt').write_text('\n'.join(report) + '\n')
    print('\n'.join(report))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inform-bin', type=Path, default=INFORM,
                        help='directory containing inform7 and inform6 executables')
    parser.add_argument('--internal', type=Path, default=INTERNAL,
                        help="Inform internal resources directory (contains Inter and Extensions)")
    parser.add_argument('--glulxe', default=GLULXE, help='path to a console Glulxe executable')
    args = parser.parse_args()
    INFORM, INTERNAL, GLULXE = args.inform_bin, args.internal, args.glulxe
    main()
