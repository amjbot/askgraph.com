#!/usr/bin/env python
import sys
import signal
import json
import time
from npu_instructions import index_insert, index_apply, ideal_render, db


wmem = {}
def signal_forget(signum,frame):
    wmem = {}
def signal_remember(signum,frame):
    print json.dumps(wmem)


def main():
    signal.signal(signal.SIGUSR1, signal_forget)
    signal.signal(signal.SIGUSR2, signal_remember)
    for arg in sys.argv[1:]:
        if arg.startswith('-'):
            continue
        for line in open(arg):
            if line.startswith('#') or line.strip()=='': continue
            symbol,require,effects = json.loads(line)
            index_insert( symbol, require, effects )
    while True:
        c = sys.stdin.read(1)
        if c=='':
            break
        index_apply( wmem, c )
    return wmem


if __name__=="__main__":
    options = {}
    for a in sys.argv[1:]:
        if a.startswith('--'):
            if '=' in a:
                k,v = a[2:].split('=',1)
            else:
                k,v = a[2:],True
            options[k] = v
    if options.get("grok",False):
        import npu_instructions
        npu_instructions.grok_enabled = True
    main()
    print ideal_render(wmem, format=options.get("format","json"))
