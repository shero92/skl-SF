#!/usr/bin/env python3
"""Per-task cost accounting."""
import argparse
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("command")
    args = p.parse_args()
    print(args.command)

if __name__ == "__main__":
    main()
