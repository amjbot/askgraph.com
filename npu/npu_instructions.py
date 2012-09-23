grok_enabled = False
symbol_table = {}
index = {}
import json
import tornado.database

db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")


def ideal_expand( ideal, limit=30 ):
    source = json.dumps(ideal)
    l = db.query("SELECT target,ts FROM observations WHERE source=%s ORDER BY ts DESC",source)
    for i in l:
        i['ts'] = i.ts.isoformat()
    return {"source":ideal, "results":l}


def ideal_render( wmem, format ):
    if format=='json':
        return json.dumps(wmem)
    elif format=='ideal':
        if 'topic' in wmem:
            return json.dumps( ideal_expand(wmem['topic']) )
        else:
            raise Exception('Unexpected ideal query format: %s', json.dumps(wmem))
    else:
        raise Exception('Unknown npu destination: %s' % format)


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
    for i in range(len(op)):
        if op[i].startswith("$"):
            op[i] = context.get(op[i][1:],None)
    for fx in split(op,';'):
        assert len(fx)>0, fx
        if fx[0] not in symbol_table:
            print "Undefined instruction: %s" % fx[0]
            exit()
        value = symbol_table[fx[0]]( context, value, *fx[1:] )
    return value

def index_insert( symbol, require, effects ):
    index[symbol] = index.get(symbol,[]) + [(require,effects)]

def index_apply( context, symbol ):
    if symbol not in index and not grok_enabled:
        print "Undefined symbol: %s" % repr(symbol)
        exit()
    for require,effects in index.get(symbol,[]):
        if not all(napp(context,require[c],context.get(c,None)) for c in require):
           continue
        for c in effects:
            if isinstance(effects[c],list):
                r = napp(context,effects[c],context.get(c,None))
                if r is None:
                    context.pop(c,None)
                else:
                    context[c] = r
            else:
                context[c] = effects[c]
symbol_table['apply'] = index_apply


def _print( ctx, x ):
    print repr(x)
symbol_table['print'] = _print

def exists( ctx, x ):
    return True if x else False
symbol_table['exists'] = exists

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

def noun( ctx, x, y ):
    r = dict( (k,v) for (k,v) in ({
        'topic': y,
        'object': ctx.get('topic',None)
    }).items() if v is not None)
    alias = db.get("SELECT * FROM alias WHERE source=%s LIMIT 1", json.dumps(r))
    if alias:
        return json.loads(alias.target)
    else:
        return r
symbol_table['noun'] = noun
