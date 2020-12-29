#!/usr/bin/env python

import sys
import signal
import os

def get_status_bar_pid(proc):
    candidates = []
    for directory in os.listdir("/proc"):
        try:
            with open(f"/proc/{directory}/cmdline", "rb") as f:
                cmdline = f.read().decode("utf-8").split("\x00")
        except FileNotFoundError as f:
            continue
        except NotADirectoryError as f:
            continue
        for name in cmdline:
            if proc in name:
                candidates.append(directory)
    return candidates


if __name__ == "__main__":
    pid = get_status_bar_pid("status_bar.py")
    try:
        if isinstance(pid, list):
            pid = int(pid[0])
        else:
            pid = int(pid)
    except IndexError as e:
        sys.exit(0)
    os.kill(pid, signal.SIGUSR1)
