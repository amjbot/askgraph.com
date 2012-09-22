#!/usr/bin/env python

import json
import datetime
import urllib
import os
import os.path
import tornado.database
import string

db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")

#   Removed because these fields contain commas (doh!)
#   ('a5', 'Ask Size'), #WARNING THIS CONTAINS COMMAS FOR 1,000,000 markers
#   ('b6', 'Bid Size'),
#   ('k3', 'Last Trade Size'),
#   ('f6', 'Float Shares'),

#   Removed because this wastes too much space
#   ('t6', 'Trade Links'),

#{'topic': u'price', 'object': {'topic': u'stock', 'object': {'topic': u'apple'}}}

fields = [
   ('b2', 'Ask (Real-time)'),
   ('b3', 'Bid (Real-time)'),
   ('b4', 'Book Value'),
   ('d', 'Dividend/Share'),
   ('e', 'Earnings/Share'),
   ('e1', 'Error Indication (returned for symbol changed / invalid)'),
   ('h', "Day's High"),
   ('j1', 'Market Capitalization'),
   ('j4', 'EBITDA'),
   ('m', "Day's Range"),
   ('n', 'Name'),
   ('o', 'Open'),
   ('p', 'Previous Close'),
   ('p5', 'Price/Sales'),
   ('p6', 'Price/Book'),
   ('q', 'Ex-Dividend Date'),
   ('r1', 'Dividend Pay Date'),
   ('r2', 'P/E Ratio (Real-time)'),
   ('r5', 'PEG Ratio'),
   ('s', 'Symbol'),
   ('s7', 'Short Ratio'),
   ('v', 'Volume'),
   ('y', 'Dividend Yield'),
]
basedir = os.path.abspath(os.path.dirname(__file__))
all_securities = list(set([ urllib.quote(s) for s in open(basedir+"/securities.csv").read().split() if s.strip()!="" ]))
now = datetime.datetime.now()


while len(all_securities)>0:
    securities,all_securities = all_securities[:200],all_securities[200:]

    url = "http://finance.yahoo.com/d/quotes.csv?f="\
      + "".join(k for (k,v) in fields)\
      + "&s=" + "+".join(securities)
    response = urllib.urlopen(url)
    if response.getcode()!=200:
        print "Error response: "+response.getcode()
        print response.read()
        print
        break
    for line in urllib.urlopen(url).readlines():
        if line.strip()=="": continue
        quote = dict(zip([v for (k,v) in fields], line.split(',')))
        if len(quote)!=len(fields):
            print "|values|=%d != |keys|=%d !!!\n%s" % (len(quote),len(fields),line)
            continue
        if quote['Error Indication (returned for symbol changed / invalid)'] != '"N/A"':
            pass#print "No such ticker symbol: %s" % [quote['s']]
        else:
            symbol = quote['Symbol']
            if not symbol.startswith('"') or not symbol.endswith('"') or not symbol[1] in string.letters:
                continue
            for k in quote:
                key = json.dumps({ "topic": k, "object": {
                    "topic": "stock", "object": {"topic": symbol[1:-1]}
                }}).lower()
                value = quote[k].lower()
                db.execute("INSERT observations(source,target) VALUES(%s,%s)", key, value)

