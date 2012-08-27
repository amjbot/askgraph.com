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
import fjorm

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
        

class index( tornado.web.RequestHandler ):
    def get( self ):
        headers = db.query("SELECT * FROM document_headers")
        headers = map(dbrow_to_dataset,headers)
        self.render( "index.html", headers=headers )
class privacy( tornado.web.RequestHandler ):
    def get( self ):
        self.render( "privacy.html" )


class silent_work( tornado.web.RequestHandler ):
    def get( self ):
        route = self.get_argument("route",None)
        w = route and db.get("SELECT * FROM mr_workflow WHERE workflow_route=%s ORDER BY RAND() LIMIT 1", route)
        w = w or db.get("SELECT * FROM mr_workflow ORDER BY RAND() LIMIT 1")
        workflow_id = w and w.id
        route = w and w.workflow_route
        output = w and w.workflow_output
        link = w and json.loads(w.workflow_value).get('data',None)
        form = db.get("SELECT * FROM fjorm WHERE name=%s", route)
        form = form and json.loads(form.form)
        self.render("work.html", link=link, workflow_id=workflow_id, route=route, output=output, form=form)
    def post( self ):
        route = self.get_argument("route")
        output = self.get_argument("output")
        workflow_id = self.get_argument("workflow_id")
        args = dict((k,v[0]) for (k,v) in self.request.arguments.items())
        del args['_xsrf']
        del args['workflow_id']
        del args['route']
        del args['output']
        value = fjorm.parse_response( args )
        db.execute("INSERT mr_dataset(dataset_name,dataset_value) VALUES(%s,%s)", output, json.dumps(value))
        db.execute("DELETE FROM mr_workflow WHERE id=%s", workflow_id)
        self.redirect("/silent_work?route="+tornado.escape.url_escape(route))

class request( tornado.web.RequestHandler ):
    def get( self ):
        self.render("request.html")
    def post( self ):
        name = self.get_argument("name","")
        request = self.get_argument("request","")
        db.execute("INSERT requests(name,request) VALUES(%s,%s)",name,request)
        self.redirect("/")

class crawl( tornado.web.RequestHandler ):
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
       , dataset, page*perpage, perpage)
    header = dict((k,v) for (k,v) in header.items() if (len(columns)==0 or not k.startswith('col') or k in columns))
    documents = [
        dict( (k,v) for (k,v) in d.items() if (len(columns)==0 or not k.startswith('col') or k in columns) )
        for d in documents
    ]
    header_as_row = dbrow_to_tablerow(header)(header)
    documents = map(dbrow_to_tablerow(header),documents)
    return header,header_as_row,documents

PERPAGE = 300
class document( tornado.web.RequestHandler ):
    def get( self, p, q ):
        p = int(p)
        query = q.split('/')
        if len(query) < 1:
            raise tornado.web.HTTPError(400)
        meta,header,documents = query_document(query, page=p, perpage=PERPAGE)
        partial = len(documents)==PERPAGE
        self.render( "document.html", p=p, q=q, meta=meta, header=header, documents=documents, partial=partial)

class download( tornado.web.RequestHandler ):
    def get( self, p, q ):
        p = int(p)
        query = q.split('/')
        if len(query) < 1:
            raise tornado.web.HTTPError(400)
        meta,header,documents = query_document(query, page=p, perpage=PERPAGE)
        self.set_header('Content-Type', 'text/csv')
        self.set_header('Content-Disposition', 'attachment; filename='+meta["dataset"]+'.csv')
        output = ",".join( csv_repr(c.val) for c in header )
        for d in documents:
            output += "\n" + ",".join( csv_repr(c.val) for c in d )
        self.write(output)


class sitemap( tornado.web.RequestHandler ):
    def get( self ):
        loc = []
        loc.append( "http://www.askgraph.com/" )
        loc.append( "http://www.askgraph.com/privacy" )
        loc.append( "http://www.askgraph.com/request" )
        for row in db.query("SELECT *,count(*) FROM documents GROUP BY dataset"):
            for p in range(row['count(*)'] / PERPAGE):
                loc.append( "http://www.askgraph.com/d/" + str(p) + "/" + urllib.quote(row.dataset))
        self.render( "sitemap.xml", loc=loc )
