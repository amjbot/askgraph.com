import tornado.web
import tornado.database


db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")


class index( tornado.web.RequestHandler ):
    def get( self ):
        self.render( "index.html" )
    def post( self ):
        contact = self.get_argument("contact","")
        request = self.get_argument("request","")
        if not contact or not request:
            self.redirect("/?error=Invalid+request.")
        else:
            db.execute("INSERT INTO requests(contact,request) VALUES(%s,%s)", contact, request)
            self.redirect("/?success=Your+request+is+being+reviewed.")
