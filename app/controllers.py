import tornado.web
import tornado.database
import tornado.escape
import urllib
import md5
import random
import string
import logging

db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")

def dbrow_to_dataset( row ):
    dataset = row['dataset']
    return tornado.database.Row({"text":dataset , "url":"/d/"+dataset})
def dbrow_to_tablerow( row ):
    output = []
    dataset = row.pop('dataset')
    for key,value in sorted(row.items()):
        if not (key.startswith("key") or key.startswith("val")) or value=='':
            continue
        url = ("/"+key+"/") \
            + urllib.quote(value if (isinstance(value,str) or isinstance(value,unicode)) else repr(value))
        output.append(tornado.database.Row({"text": value, "url":url}))
    return output
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
        def unpack_csv( s ):
            l = []
            buffer = ''
            string_close = ''
            for c in s:
                if string_close==c:
                    string_close = ''
                elif string_close:
                    buffer += c
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
        headers = []
        documents = []
        for i,line in enumerate(file['body'].split('\n')):
            if i==0:
                headers = unpack_csv(line)
            elif line:
                documents.append( unpack_csv(line) )
        if headers and documents:
            db.execute("DELETE FROM document_headers WHERE dataset=%s", dataset)
            db.execute("DELETE FROM documents WHERE dataset=%s", dataset)
            db.execute("INSERT document_headers(dataset," + \
                       ",".join( ("key"+str(i)) for i in range(len(headers)) ) + \
                       ") VALUES(" + \
                       ",".join( "%s" for i in range(len(headers)+1) ) + \
                       ")", dataset, *headers)
            for d in documents:
                db.execute("INSERT documents(dataset," + \
                           ",".join( ("val"+str(i)) for i in range(len(headers)) ) + \
                           ") VALUES (" + \
                           ",".join( "%s" for i in range(len(headers)+1) ) + \
                           ")", dataset, *d)
        self.redirect("/d/"+dataset)


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


def query_document( doc ):
    header = db.get("SELECT * FROM document_headers WHERE dataset=%s", doc[0])
    dataset = header['dataset']
    documents = db.query("SELECT * FROM documents WHERE dataset=%s", doc[0])
    #documents = db.query("SELECT * FROM documents WHERE dataset=%s AND " +
    #   " AND ".join( ("%s=val"+str(i)) for i in range(len(doc)-1) ), *doc)
    header = dbrow_to_tablerow(header)
    documents = map(dbrow_to_tablerow,documents)
    return dataset,header,documents

class document( BaseHandler ):
    def get( self, q ):
        query = q.split('/')
        if len(query) < 1:
            raise tornado.web.HTTPError(400)
        dataset,header,documents = query_document(query)
        self.render( "document.html", q=q, dataset=dataset, header=header, documents=documents)

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

