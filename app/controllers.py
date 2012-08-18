import tornado.web
import tornado.database
import tornado.escape
import urllib
import md5
import random
import string
import logging
import sys
import simplejson as json

db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")

def dbrow_to_dataset( row ):
    dataset = row['dataset']
    return tornado.database.Row({"key":dataset , "val":dataset})
def dbrow_to_tablerow( header ):
    def inner( row ):
        output = []
        dataset = row['dataset']
        for key,val in sorted(row.items()):
            if not key.startswith("col") or header[key]=="":
                continue
            key = header[key]
            key = key if (isinstance(key,str) or isinstance(key,unicode)) else repr(key)
            val = val if (isinstance(val,str) or isinstance(val,unicode)) else repr(val)
            output.append(tornado.database.Row({"key": key, "val":val}))
        return output
    return inner
def csv_repr( v ):
    if not (isinstance(v,str) or isinstance(v,unicode)):
        return repr(v)
    else:
        return '"' + v.replace('"','\\"') + '"'
        

class BaseHandler( tornado.web.RequestHandler ):
    pass

class _404( BaseHandler ):
    def get( self ):
        self.render("404.html")

class index( BaseHandler ):
    def get( self ):
        headers = db.query("SELECT * FROM document_headers")
        headers = map(dbrow_to_dataset,headers)
        self.render( "index.html", headers=headers )
class privacy( BaseHandler ):
    def get( self ):
        self.render( "privacy.html" )


class silent_work( BaseHandler ):
    def get( self ):
        route = self.get_argument("route")
        link = db.get("SELECT * FROM mr_workflow WHERE workflow_route=%s ORDER BY RAND() LIMIT 1", route)
        form = db.get("SELECT * FROM fjorm WHERE name=%s", route)
        form = form and json.loads(form.form)
        self.render("work.html", link=link, form=form)
    def post( self ):
        link = self.get_argument("link")
        key = self.get_argument("key")
        value = self.get_argument("value")
        db.execute("INSERT (note_link,note_key,note_value) VALUES(%s,%s,%s)", link, key, value)

class request( BaseHandler ):
    def get( self ):
        self.render("request.html")
    def post( self ):
        name = self.get_argument("name","")
        request = self.get_argument("request","")
        db.execute("INSERT requests(name,request) VALUES(%s,%s)",name,request)
        self.redirect("/")

class crawl( BaseHandler ):
    def check_xsrf_cookie( self ):
        pass
    def post( self ):
        source = self.get_argument("source")
        target = self.get_argument("target")
        db.execute("INSERT arrows(source,target) VALUES(%s,%s)",source,target)

def query_document( doc, page=0, perpage=999999 ):
    dataset = doc[0]
    query = doc[1:]
    rows = {}
    columns = set()
    for q in query:
        if ':' in q:
            k,v = q.split(':',1)
            rows[k] = v
        else:
            columns.add(q)
    header = db.get("SELECT * FROM document_headers WHERE dataset=%s", dataset)
    rheader = dict((v,k) for (k,v) in header.items())
    columns = set(rheader[k] for k in columns)
    documents = db.query("SELECT * FROM documents WHERE dataset=%s"\
       + ("" if len(rows)==0 else " AND ")\
       + " AND ".join( rheader[k]+"="+json.dumps(v) for (k,v) in rows.items() if k in rheader )\
       + " LIMIT %s,%s"
       , dataset, page*perpage, (page+1)*perpage)
    header = dict((k,v) for (k,v) in header.items() if (len(columns)==0 or not k.startswith('col') or k in columns))
    documents = [
        dict( (k,v) for (k,v) in d.items() if (len(columns)==0 or not k.startswith('col') or k in columns) )
        for d in documents
    ]
    header_as_row = dbrow_to_tablerow(header)(header)
    documents = map(dbrow_to_tablerow(header),documents)
    return header,header_as_row,documents

PERPAGE = 300
class document( BaseHandler ):
    def get( self, q ):
        query = q.split('/')
        if len(query) < 1:
            raise tornado.web.HTTPError(400)
        meta,header,documents = query_document(query, page=0, perpage=PERPAGE)
        partial = len(documents)==PERPAGE
        self.render( "document.html", q=q, meta=meta, header=header, documents=documents, partial=partial)
class document_page( BaseHandler ):
    def get( self, p, q ):
        query = q.split('/')
        if len(query) < 1:
            raise tornado.web.HTTPError(400)
        meta,header,documents = query_document(query, page=int(p), perpage=PERPAGE)
        partial = len(documents)==PERPAGE
        self.render( "document_page.html", q=q, meta=meta, header=header, documents=documents, partial=partial)

class download( BaseHandler ):
    def get( self, q ):
        query = q.split('/')
        if len(query) < 1:
            raise tornado.web.HTTPError(400)
        dataset,header,documents = query_document(query)
        self.set_header('Content-Type', 'text/csv')
        self.set_header('Content-Disposition', 'attachment; filename='+dataset+'.csv')
        output = ",".join( csv_repr(c.text) for c in header )
        for d in documents:
            output += "\n" + ",".join( csv_repr(c.text) for c in d )
        self.write(output)

