symbol_table = {}

def _print( x ):
    print repr(x)
symbol_table['print'] = _print

def clear( x ):
    return None
symbol_table['clear'] = clear

def error( x, y ):
    print "Error:", y
    exit(1)
symbol_table['error'] = error

def __add__( x, y ):
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

