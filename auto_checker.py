#!/usr/bin/env python3
"""Watch a text file and run the checker when its contents change.

This mode never edits or archives the input. A change rechecks the entire file,
so use it only for small, authorized account lists.
"""
import argparse
import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def file_digest(path):
    try:
        with open(path, 'rb') as source:
            digest = hashlib.sha256()
            for block in iter(lambda: source.read(65536), b''):
                digest.update(block)
            return digest.digest()
    except FileNotFoundError:
        return None


def run_checker(input_file):
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / 'atr3.py'), '-i', str(Path(input_file).resolve())],
            cwd=SCRIPT_DIR, timeout=3600,
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f'[ERROR] Checker failed: {exc}')
        return False


def monitor_file(input_file='input.txt', check_interval=5):
    if check_interval <= 0:
        raise ValueError('Interval must be positive')
    print(f'[INFO] Watching {input_file}; each change rechecks the entire file. Ctrl+C to stop.')
    last_digest = file_digest(input_file)
    try:
        while True:
            time.sleep(check_interval)
            current = file_digest(input_file)
            if current is None or current == last_digest:
                continue
            print('[INFO] Change detected; checking without modifying the input.')
            if run_checker(input_file):
                # If the source changed during the run, process the new contents next time.
                last_digest = current
            else:
                print('[ERROR] Run failed; will retry on the next interval.')
    except KeyboardInterrupt:
        print('\n[INFO] Monitor stopped.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor a text file for changes')
    parser.add_argument('-i', '--input', default='input.txt')
    parser.add_argument('-t', '--interval', type=int, default=5)
    args = parser.parse_args()
    if args.interval <= 0:
        parser.error('interval must be positive')
    monitor_file(args.input, args.interval)
