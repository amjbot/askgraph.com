import tornado.web
import tornado.database
import json


db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")


def can_json( o ):
    try:
       json.dumps(o)
       return True
    except:
       return False 


class index( tornado.web.RequestHandler ):
    def get( self ):
        self.render( "index.html" )
    def post( self ):
        contact = self.get_argument("contact","")
        request = self.get_argument("request","")
        context = json.dumps(dict( (k,v) for (k,v) in vars(self.request).items() if can_json(v) ))
        if not contact or not request:
            self.redirect("/?error=Invalid+request.")
        else:
            db.execute("INSERT INTO requests(contact,request,context) VALUES(%s,%s,%s)", contact, request, context)
            self.redirect("/?success=Your+request+is+being+reviewed.")
