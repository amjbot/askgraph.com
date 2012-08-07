import tornado.web
import tornado.database
import md5
import random
import string
import smtplib
import logging
from email.mime.text import MIMEText

db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")

def dbrow_to_dataset( row ):
    dataset = row['dataset']
    return tornado.database.Row({"text":dataset , "url":"/d/"+dataset})
def dbrow_to_tablerow( row ):
    #input  = { dataset:?, key0:?, key1:?, ... }
    #       | { dataset:?, val0:?, val1:?, ... }
    #output = [{ url:?, text:? }]
    output = []
    dataset = row.pop('dataset')
    url_prefix = '/d/'+dataset
    for key,value in sorted(row.items()):
        url_prefix += ("/k/" if key.startswith("key") else "/v/") + repr(value)
        output.append(tornado.database.Row({"text": value, "url":url_prefix}))
    return output

class BaseHandler( tornado.web.RequestHandler ):
    def get_current_user( self ):
        return self.get_secure_cookie("user")

class index( BaseHandler ):
    def get( self ):
        headers = db.query("SELECT * FROM document_headers")
        headers = map(dbrow_to_dataset,headers)
        self.render( "index.html", headers=headers )

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
                l.append( buffer )
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

class document( BaseHandler ):
    def get( self, doc ):
        doc = doc.split('/')
        if len(doc) < 1:
            raise tornado.web.HTTPError(400)
        header = db.get("SELECT * FROM document_headers WHERE dataset=%s", doc[0])
        documents = db.query("SELECT * FROM documents WHERE dataset=%s", doc[0])
        dataset = header['dataset']
        header = [ header['key'+str(i)] for i in range(len(header)-2) ]
        documents = [ [d['val'+str(i)] for i in range(len(header)-2)] for d in documents ]
        #documents = db.query("SELECT * FROM documents WHERE dataset=%s AND " +
        #   " AND ".join( ("%s=val"+str(i)) for i in range(len(doc)-1) ), *doc)
        self.render( "document.html", dataset=dataset, header=header, documents=documents)
