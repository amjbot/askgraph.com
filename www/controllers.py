import tornado.web
import tornado.database
import tornado.escape
import random
import string
import json
import hashlib
import sys
import time

db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")


class index( tornado.web.RequestHandler ):
    def get( self ):
        self.render( "index.html" )
    def post( self ):
        email = self.get_argument("email","")
        request = self.get_argument("request","")
        if not email or not request:
            self.redirect("/?error=Invalid+request.")
        else:
            db.execute("INSERT INTO requests(email,request) VALUES(%s,%s)", email, request)
            self.redirect("/?success=Your+request+is+being+reviewed.")
        raise tornado.web.HTTPError(404)
