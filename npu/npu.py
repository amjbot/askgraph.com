#!/usr/bin/env python
import sys
import signal
import json
import time
from npu_instructions import index_insert, index_apply


wmem = {}
def signal_forget(signum,frame):
    wmem = {}
def signal_remember(signum,frame):
    print json.dumps(wmem)


def main():
    signal.signal(signal.SIGUSR1, signal_forget)
    signal.signal(signal.SIGUSR2, signal_remember)
    for arg in sys.argv[1:]:
        for line in open(arg):
            if line.startswith('#') or line.strip()=='': continue
            symbol,require,effects = json.loads(line)
            index_insert( symbol, require, effects )
    while True:
        print wmem
        c = sys.stdin.read(1)
        if c=='':
            break
        index_apply( wmem, c )


if __name__=="__main__":
    main()

