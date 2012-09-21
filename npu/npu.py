#!/usr/bin/env python
import sys
import signal
import json
import time


wmem = [{}]
index = {}


def signal_forget(signum,frame):
    wmem = []
def signal_remember(signum,frame):
    print json.dumps(wmem)


def null_step( symbol ):
    return []


def main():
    signal.signal(signal.SIGUSR1, signal_forget)
    signal.signal(signal.SIGUSR2, signal_remember)
    for arg in sys.argv[1:]:
        for line in open(arg):
            symbol,context,effects = json.loads(line)
            index[symbol] = (context,effects)
    while True:
        c = sys.stdin.read(1)
        f = index.get(c,null_step(c))
        nmem = []
        for image in wmem:
            for step in f:
                nmem += step(image)
        wmem = nmem


if __name__=="__main__":
    main()

