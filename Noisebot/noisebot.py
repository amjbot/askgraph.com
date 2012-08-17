#!/usr/bin/env python

import tornado.database
import tornado.httpclient
import sys
import imp
import datetime
import bs4
import re
import urlparse
import time

db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")

target_ContentType = {
   "html": set(["text/html"]),
   "pdf": set(["application/pdf"]),
}

def crawl( url, target=None, depth=1, noisy=False ):
    sources = set([ url ])
    visited = set()
    matched = set()
    content_type = {}
    http_client = tornado.httpclient.HTTPClient()
    for _ in range(depth+1):
        for url in list(sources):
            if url in visited:
                continue
            time.sleep(1)
            visited.add( url )
            try:
                response = http_client.fetch(url, user_agent="noisebot")
                content_type[url] = response.headers.get('Content-Type','text/html').split(';')[0].strip()
                if content_type[url] == 'text/html':
                    soup = bs4.BeautifulSoup(response.body)
                    for a in soup.find_all("a"):
                        href = a.get("href")
                        if not href:
                           continue
                        if not href.startswith("http"):
                           href = urlparse.urljoin( urlparse.urlsplit(url).geturl(), href )
                        sources.add( href )
                        if noisy:
                            print "Extract content from resource at %s" % (href,)
            except tornado.httpclient.HTTPError, e:
                if noisy:
                    import traceback
                    print "Caught exception while trying to crawl %s" % item.route
                    traceback.print_exc()
    for url in visited:
        if not target or content_type[url] in target_ContentType[target]:
            matched.add(url)
    return list(matched)

if __name__=="__main__" and (sys.argv[1].startswith('http://') or sys.argv[1].startswith('https://')):
    kwargs = {}
    for a in sys.argv[2:]:
        k,v = a.split('=',1)
        kwargs[k] = v
    print crawl(sys.argv[1], noisy=True, **kwargs)
