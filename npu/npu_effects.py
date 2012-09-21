
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

