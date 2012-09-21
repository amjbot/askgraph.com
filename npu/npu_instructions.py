
symbol_table = {}
index = {}


def split( list, sep ):
    r = [[]]
    for item in list:
        if item==sep:
            r.append([])
        else:
            r[-1].append( item )
    return r
def napp( context, op, value ):
    assert isinstance(context,dict)
    for fx in split(op,';'):
        assert len(fx)>0, fx
        assert fx[0] in symbol_table, fx[0]
        r = symbol_table[fx[0]]( context, value, *fx[1:] )
    return r

def index_insert( symbol, require, effects ):
    index[symbol] = index.get(symbol,[]) + [(require,effects)]

def index_apply( context, symbol ):
    for require,effects in index.get(symbol,[]):
        if not all(napp(context,require[c],context.get(c,None)) for c in require):
           continue
        for c in effects:
            r = napp(context,effects[c],context.get(c,None))
            if r is None:
                context.pop(c,None)
            else:
                context[c] = r
symbol_table['apply'] = index_apply


def _print( ctx, x ):
    print repr(x)
symbol_table['print'] = _print

def clear( ctx, x ):
    return None
symbol_table['clear'] = clear

def error( ctx, x, y ):
    print "Error:", y
    exit(1)
symbol_table['error'] = error

def __add__( ctx, x, y ):
    if isinstance(y,str) or isinstance(y,unicode):
        return (x or '') + y
    elif isinstance(y,int):
        return (x or 0) + y
    elif isinstance(y,float):
        return (x or 0.0) + y
    elif isinstance(y,list):
        return (x or []) + y
    elif isinstance(y,dict):
        x = dict((x or {}).items())
        x.update( y )
        return x
    else: assert False
symbol_table['+'] = __add__

