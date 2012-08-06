import tornado.web
import tornado.database
import md5
import random
import string
import smtplib
import logging
from email.mime.text import MIMEText

db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")

class index( tornado.web.RequestHandler ):
    def get( self ):
        headers = db.query("SELECT * FROM document_headers")
        self.render( "document.html", documents=headers )

class upload( tornado.web.RequestHandler ):
    def get( self ):
        self.render( "upload.html" )
    def post( self ):
        logging.warn( str(self.request.headers) )
        raise tornado.web.HTTPError(401)

class document( tornado.web.RequestHandler ):
    def get( self, doc ):
        doc = doc.split('/')
        if len(doc) < 1:
            raise tornado.web.HTTPError(400)
        while len(doc) < 11:
            doc.append( '' )
        header = db.get("SELECT * FROM document_headers WHERE dataset=%s", doc[0])
        documents = db.query("SELECT * FROM documents WHERE dataset=%s AND "
           "(%s IN (val0,'') AND (%s IN (val1,'') AND (%s IN (val2,'') AND "
           "(%s IN (val3,'') AND (%s IN (val4,'') AND (%s IN (val5,'') AND "
           "(%s IN (val6,'') AND (%s IN (val7,'') AND (%s IN (val8,'') AND "
           "(%s IN (val9,'')", *doc)
        self.render( "document.html", header=header, documents=documents)
