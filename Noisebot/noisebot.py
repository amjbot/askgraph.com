#!/usr/bin/env python

import tornado.database
import tornado.httpclient
import sys
import imp
import datetime
import bs4
import re
import urlparse

db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")

def crawl( LIMIT=100, noisy=False ):
    http_client = tornado.httpclient.HTTPClient()
    i = 0
    for i,item in enumerate(db.query("SELECT * FROM noisebot_input WHERE DATE_ADD(previous_crawl,INTERVAL 7 DAY)<now() LIMIT %s", LIMIT)):
        try:
            response = http_client.fetch(item.source, user_agent="noisebot")
            soup = bs4.BeautifulSoup(response.body)
            for a in soup.find_all("a"):
                href = a.get("href")
                if not href:
                    continue
                if not href.startswith("http"):
                    href = urlparse.urljoin( urlparse.urlsplit(item.source).geturl(), href )
                db.execute("INSERT IGNORE noisebot_output(link,route) VALUES(%s,%s)", href, item.route)
                if noisy:
                    print "Extract url %s from source %s" % (href, item.source)
        except tornado.httpclient.HTTPError, e:
            if noisy:
                import traceback
                print "Caught exception while trying to crawl %s" % item.route
                traceback.print_exc()
        db.execute("UPDATE noisebot_input SET previous_crawl=now() WHERE id=%s", item.id)
    return i

if __name__=="__main__":
    crawl(noisy=True)
