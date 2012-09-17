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
        raise tornado.web.HTTPError(404)
