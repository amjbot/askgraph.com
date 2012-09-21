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
    return [ ({},['error', "Invalid character: %s." % repr(symbol)]) ]
def null_wmem():
    print "Dead end."
    exit()

import npu_effects
effects = {
  '+': npu_effects.__add__,
}


def split( list, sep ):
    r = [[]]
    for item in list:
        if item==sep:
            r.append([])
        else:
            r[-1].append( item ) 
    return r
def napp( op, value ):
    for fx in split(op,';'):
        assert len(fx)>0, fx
        assert fx[0] in effects, fx[0]
        r = effects[fx[0]]( value, *fx[1:] )
    return r


def main():
    global wmem
    signal.signal(signal.SIGUSR1, signal_forget)
    signal.signal(signal.SIGUSR2, signal_remember)
    for arg in sys.argv[1:]:
        for line in open(arg):
            if line.startswith('#') or line.strip()=='': continue
            symbol,context,effects = json.loads(line)
            index[symbol] = index.get(symbol,[]) + [(context,effects)]
    while True:
        print wmem
        c = sys.stdin.read(1)
        if c=='':
            break
        f = index.get(c,null_step(c))
        nmem = []
        for image in wmem:
            for context,effect in f:
                if not all(napp(context[c],image.get(c,None)) for c in context):
                    continue
                nimage = dict(image.items())
                for c in effect:
                    r = napp(effect[c],nimage.get(c,None))
                    if r is None:
                        nimage.pop(c,None)
                    else:
                        nimage[c] = r
                nmem.append( nimage )
        wmem = nmem
        if len(wmem)==0:
            null_wmem()


if __name__=="__main__":
    main()

