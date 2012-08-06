import app.controllers as controllers
import os.path

import tornado.web
import tornado.httpserver
import tornado.ioloop

import sys

settings = dict(
   cookie_secret  =  "34qw4x65cdf7vgy7buhnijmk9xrcdtfvyugbihn",
   static_path    = os.path.join(os.path.dirname(__file__), "static"),
   template_path  = os.path.join(os.path.dirname(__file__), "views"),
)

application = tornado.web.Application( [
    ( "^/",                      controllers.index        ),
    ( "^/d/(?P<doc>.+)",         controllers.document     ),
], **settings )


if __name__=="__main__":
    tornado.httpserver.HTTPServer(application, xheaders=True ).listen( 80 )
    tornado.ioloop.IOLoop.instance().start()
