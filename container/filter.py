#!/usr/bin/env python3

import sys

ok_paths = [
    "GET / ",
    "/writing",
    "/coding",
    "/reviews",
    "/tags",
    "/about",
    "/page",
    "/categories",
]

if __name__ == '__main__':
    for line in sys.stdin.readlines():
        if not any(ok in line for ok in ok_paths):
            continue
        print(line, end='', flush=True)
