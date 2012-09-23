#!/usr/bin/env python

import datetime
import tornado.database
import subprocess


db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")


#datetime.datetime.strptime( "2007-03-04T21:08:12", "%Y-%m-%dT%H:%M:%S" )


new_conversations = db.query("SELECT * FROM requests ORDER BY ts DESC LIMIT 20")
for r in new_conversations:
    p = subprocess.Popen("npu --language=english --output=ideal",shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    p.stdin.write( r.request )
    p.stdin.close()
    p.wait()
    ideal = p.stdout.read()
    print "process converation:", r.request
    print "npu", ideal
    #if response not empty, then route to outgoing messages
