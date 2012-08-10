#!/usr/bin/env python

import app.controllers as controllers
import os.path
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.process
import sys

settings = dict(
   cookie_secret  =  "34qw4x65cdf7vgy7buhnijmk9xrcdtfvyugbihn",
   static_path    = os.path.join(os.path.dirname(__file__), "static"),
   template_path  = os.path.join(os.path.dirname(__file__), "views"),
   xsrf_cookies   = True,
   login_url      = "/authenticate",
)

application = tornado.web.Application( [
    ( "^/",                          controllers.index         ),
    ( "^/privacy",                   controllers.privacy       ),
    ( "^/upload",                    controllers.upload        ),
    ( "^/authenticate",              controllers.authenticate  ),
    ( "^/signout",                   controllers.signout       ),
    ( "^/d/(?P<q>.+)",               controllers.document      ),
    ( "^/p/(?P<p>[0-9]+)/(?P<q>.+)", controllers.document_page ),
    ( "^/download/(?P<q>.+)",        controllers.download      ),
], **settings )


if __name__=="__main__":
    tornado.process.fork_processes(0)
    tornado.httpserver.HTTPServer(application, xheaders=True ).listen( 80 )
    tornado.ioloop.IOLoop.instance().start()
