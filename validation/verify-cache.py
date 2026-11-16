import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

parser = argparse.ArgumentParser(description='Run unified-cache tests in separate processes')
parser.add_argument('repository', type=Path)
parser.add_argument('--target')
args = parser.parse_args()
command = ['cargo', 'test', '-p', 'vesuvius-rs', '--lib', '--locked', '--no-run', '--message-format=json', '-j3']
if args.target:
    command += ['--target', args.target]
build = subprocess.run(command, cwd=args.repository, stdout=subprocess.PIPE, text=True, encoding='utf-8', check=True)
artifacts = [json.loads(line) for line in build.stdout.splitlines() if line.startswith('{')]
binary = next(row['executable'] for row in artifacts if row.get('reason') == 'compiler-artifact' and row.get('target', {}).get('name') == 'vesuvius_rs' and row.get('profile', {}).get('test') and row.get('executable'))
listed = subprocess.check_output([binary, 'cache::', '--list', '--format', 'terse'], text=True, encoding='utf-8')
names = [line.removesuffix(': test') for line in listed.splitlines() if line.endswith(': test')]
assert names, 'No cache tests found'
passed = ignored = 0
with tempfile.TemporaryDirectory(prefix='vesuvius-cache-tests-') as directory:
    scratch = Path(directory).resolve()
    assert scratch.parent == Path(tempfile.gettempdir()).resolve()
    environment = os.environ.copy()
    environment.update({'TEMP': str(scratch), 'TMP': str(scratch), 'TMPDIR': str(scratch)})
    for index, name in enumerate(names, 1):
        result = subprocess.run([binary, name, '--exact', '--test-threads=1'], cwd=args.repository, env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', timeout=90)
        print(f'{index}/{len(names)}: {name}', flush=True)
        sys.stdout.write(result.stdout)
        assert result.returncode == 0, f'Test failed: {name}'
        counts = re.search(r'test result: ok\. (\d+) passed; 0 failed; (\d+) ignored', result.stdout)
        assert counts, f'Missing test result: {name}'
        passed += int(counts[1])
        ignored += int(counts[2])
assert not scratch.exists(), 'Temporary test directory was not removed'
print(f'Cache validation: {passed} passed, {ignored} ignored', flush=True)
