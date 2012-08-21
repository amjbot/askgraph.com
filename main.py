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
   xsrf_cookies   = True
)

application = tornado.web.Application( [
    ( "^/",                          controllers.index         ),
    ( "^/privacy",                   controllers.privacy       ),
    ( "^/request",                   controllers.request       ),
    #( "^/d/(?P<q>.+)",               controllers.document      ),
    ( "^/p/(?P<p>[0-9]+)/(?P<q>.+)", controllers.document_page ),
    ( "^/download/(?P<q>.+)",        controllers.download      ),
    ( "^/silent_bot_crawl",          controllers.crawl         ),
    ( "^/silent_work",               controllers.silent_work   ),
    ( ".*",                          controllers._404          ),
], **settings )


if __name__=="__main__":
    tornado.process.fork_processes(0)
    tornado.httpserver.HTTPServer(application, xheaders=True ).listen( 80 )
    tornado.ioloop.IOLoop.instance().start()
