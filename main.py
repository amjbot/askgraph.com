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
   xsrf_cookies   = True,
   login_url      = "/authenticate",
)

application = tornado.web.Application( [
    ( "^/",                      controllers.index        ),
    ( "^/upload",                controllers.upload       ),
    ( "^/authenticate",          controllers.authenticate ),
    ( "^/d/(?P<q>.+)",           controllers.document     ),
    ( "^/download/(?P<q>.+)",    controllers.download     ),
], **settings )


if __name__=="__main__":
    tornado.httpserver.HTTPServer(application, xheaders=True ).listen( 80 )
    tornado.ioloop.IOLoop.instance().start()
