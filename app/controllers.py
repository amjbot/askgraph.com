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
            if not key.startswith("col"):
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
    def get_current_user( self ):
        return self.get_secure_cookie("user")

class index( BaseHandler ):
    def get( self ):
        headers = db.query("SELECT * FROM document_headers")
        headers = map(dbrow_to_dataset,headers)
        self.render( "index.html", headers=headers )
class privacy( BaseHandler ):
    def get( self ):
        self.render( "privacy.html" )

class upload( BaseHandler ):
    @tornado.web.authenticated
    def get( self ):
        self.render( "upload.html" )
    @tornado.web.authenticated
    def post( self ):
        if self.current_user!="karmafeeder":
            raise tornado.web.HTTPError(403)
        def unpack_csv( s ):
            l = []
            buffer = ''
            escape = False
            string_close = ''
            for c in s:
                if string_close==c:
                    string_close = ''
                elif string_close:
                    buffer += c
                elif c=='\\':
                    escape = True
                elif escape:
                    buffer += c
                    escape = False
                elif c=='"':
                    string_close = '"'
                elif c==',':
                    l.append( buffer )
                    buffer = ''
                else:
                    buffer += c
            if buffer:
                l.append( buffer.strip() )
            return l
        file = self.request.files['file'][0]
        if file['content_type'] != 'text/csv':
            raise HTTPError(415)
        dataset = file['filename'].split('.')[0]
        meta = {}
        headers = []
        documents = []
        for line in file['body'].split('\n'):
            if ":\t" in line:
                key,val = line.strip().split(":\t")
                meta[key] = val
            elif 'parse_headers' not in meta:
                headers = unpack_csv(line)
                meta['parse_headers'] = True
            elif line:
                documents.append( unpack_csv(line) )
        if headers and documents:
            db.execute("DELETE FROM document_headers WHERE dataset=%s", dataset)
            db.execute("DELETE FROM documents WHERE dataset=%s", dataset)
            db.execute("INSERT document_headers(dataset,source,sourcename," + \
                       ",".join( ("col"+str(i)) for i in range(len(headers)) ) + \
                       ") VALUES(" + \
                       ",".join( "%s" for i in range(len(headers)+3) ) + \
                       ")", dataset, meta.get("source",""), meta.get("sourcename",""), *headers)
            for d in documents:
                db.execute("INSERT documents(dataset," + \
                           ",".join( ("col"+str(i)) for i in range(len(headers)) ) + \
                           ") VALUES (" + \
                           ",".join( "%s" for i in range(len(headers)+1) ) + \
                           ")", dataset, *d)
        self.redirect("/d/"+urllib.quote(dataset))


class request( BaseHandler ):
    def get( self ):
        self.render("request.html")
    def post( self ):
        name = self.get_argument("name","")
        request = self.get_argument("request","")
        db.execute("INSERT requests(name,request) VALUES(%s,%s)",name,request)
        self.redirect("/")

class signout( BaseHandler ):
    def get( self ):
        self.clear_cookie("user")
        self.redirect( self.request.headers.get('Referer','/') )
class authenticate( BaseHandler ):
    def get( self ):
        next = self.get_argument("next","/")
        self.render( "authenticate.html", next=next )
    def post( self ):
        next = self.get_argument("next","/") or "/"
        name = self.get_argument("name")
        password = self.get_argument("pass")
        self.set_secure_cookie("user",name)
        self.redirect(next)


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

