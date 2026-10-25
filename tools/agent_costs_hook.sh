#!/bin/sh
# Portable launcher for Git Bash on Windows and POSIX shells.
# Does not install Python. stdin (hook JSON) passes through unchanged.
set -eu
if command -v py >/dev/null 2>&1 && py -3 -c "import sys; assert sys.version_info >= (3, 10)" >/dev/null 2>&1; then
    exec py -3 tools/agent_costs.py "$@"
elif command -v python3 >/dev/null 2>&1 && python3 -c "import sys; assert sys.version_info >= (3, 10)" >/dev/null 2>&1; then
    exec python3 tools/agent_costs.py "$@"
elif command -v python >/dev/null 2>&1 && python -c "import sys; assert sys.version_info >= (3, 10)" >/dev/null 2>&1; then
    exec python tools/agent_costs.py "$@"
else
    echo "Agent cost hooks require Python 3.10+. On Windows check: py -3 --version; install Python from python.org if missing." >&2
    exit 127
fi
