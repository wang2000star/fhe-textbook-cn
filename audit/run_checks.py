#!/usr/bin/env python3
"""Run every academic counterexample/regression script from a fixed repository root."""
from pathlib import Path
import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--without-python-demo', action='store_true',
                        help='skip the code checks that require the demo dependencies')
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    checks = sorted(directory.glob('check_*.py'))
    if args.without_python_demo:
        checks = [p for p in checks if p.name != 'check_python.py']
    failures = []
    for path in checks:
        print(f'\n=== {path.name} ===', flush=True)
        try:
            result = subprocess.run([sys.executable,str(path)],cwd=directory.parent,timeout=120)
            if result.returncode:
                failures.append(path.name)
        except subprocess.TimeoutExpired:
            print(f'FAILED: {path.name} exceeded its time limit',file=sys.stderr)
            failures.append(path.name)
    if failures:
        print('Failed checks: '+', '.join(failures),file=sys.stderr)
        return 1
    print(f'All {len(checks)} check scripts passed. This is not a cryptographic security proof.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
