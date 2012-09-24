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
    for fx in split(op,';'):
        assert len(fx)>0, fx
        if isinstance(fx[0],str) or isinstance(fx[0],unicode):
            if fx[0] not in symbol_table:
                print "Undefined instruction: %s" % fx[0]
                exit()
            value = symbol_table[fx[0]]( context, value, *fx[1:] )
        else:
            value = fx[0]
    return value

def index_insert( symbol, require, effects ):
    index[symbol] = index.get(symbol,[]) + [(require,effects)]

def beta_reduce( context, term ):
    if isinstance(term,str) or isinstance(term,unicode):
        if term.startswith("$"):
            c = context
            for t in term[1:].split("."):
                if isinstance(c,dict):
                    c = c.get(t,None)
                else:
                    c = None
            term = c
    elif isinstance(term,list):
        term = term
        for i in range(len(term)):
            term[i] = beta_reduce(context,term[i])
    elif isinstance(term,dict):
        term = term
        for k in term:
            term[k] = beta_reduce(context,term[k])
    return term
    

def _lookup( ctx, key ):
    for k in key.split("."):
        if isinstance(ctx,dict):
            ctx = (ctx or {}).get(k,None)
        else:
            ctx = None
    return ctx
def _reduce( ctx ):
    if isinstance(ctx,dict):
        for k in ctx.keys():
            ctx[k] = _reduce(ctx[k])
        for k in ctx.keys():
            if ctx[k] is None:
                ctx.pop(k)
    return ctx
def _assign( ctx, key, val ):
    for k in key.split(".")[:-1]:
        if isinstance(ctx,dict):
            ctx = (ctx or {}).get(k,None)
        else:
            ctx = None
    if isinstance(ctx,dict):
        ctx[key.split(".")[-1]] = val
    _reduce(ctx)
def _test( context, require ):
    if '||' in context:
        context.pop('||')
        join = lambda x,y: x or y
        accept = False
    else:
        join = lambda x,y: x and y
        accept = True
    for c in require:
        if isinstance(require[c],list):
            accept = join( accept, napp(context,require[c],_lookup(context,c)) )
        elif isinstance(require[c],dict):
            accept = join( accept, _test(context,require[c]) )
        else:
            accept = join( accept, require[c]==_lookup(context,c) )
    return accept

def index_apply( context, symbol ):
    #print 'apply', symbol, context
    context = beta_reduce(context,context)
    if isinstance(symbol,dict):
        symbol = [{},symbol]
    elif isinstance(symbol,list):
        pass
    elif symbol not in index and not grok_enabled:
        exit()
    else:
        symbol = index.get(symbol,[])
    for k in context:
        if k.startswith('apply:'):
            symbol.append( ({},context[k]) )
        elif k.startswith('require:'):
            symbol.append( (context[k],context.get('effect:'+k.split(':',1)[1],{})) )
    for require,effects in symbol:
        assert isinstance(require,dict), require
        assert isinstance(effects,dict), effects
        if not _test(context,require):
            continue
        require = beta_reduce(context,require)
        if not _test(context,require):
            context
        effects = beta_reduce(context,effects)
        for c in effects:
            if isinstance(effects[c],list):
                r = napp(context,effects[c],_lookup(context,c))
                if r is None:
                    _assign(context,c,None)
                else:
                    _assign(context,c,r)
            else:
                _assign(context,c,effects[c])
    #print 'return', symbol, context
    return _reduce(context)
symbol_table['apply'] = index_apply



def context( ctx, x, y ):
    return _lookup(ctx,y)
symbol_table['context'] = context

def _print( ctx, x ):
    print repr(x)
symbol_table['print'] = _print

def exists( ctx, x ):
    return True if x else False
symbol_table['exists'] = exists

def empty( ctx, x ):
    return False if x else True
symbol_table['empty'] = empty

def clear( ctx, x ):
    return None
symbol_table['clear'] = clear

def error( ctx, x, y ):
    print "Error:", y
    exit(1)
symbol_table['error'] = error

def neq( ctx, x, y ):
    return x != y
symbol_table['!='] = neq


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
    r = _reduce({
        'topic': y,
        'pos': 'noun',
        'object': ctx.get('topic',None)
    })
    alias = db.get("SELECT * FROM alias WHERE source=%s LIMIT 1", json.dumps(r))
    if alias:
        return json.loads(alias.target)
    else:
        return r
symbol_table['noun'] = noun
