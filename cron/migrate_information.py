#!/usr/bin/env python

import tornado.database
db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")


db.execute("INSERT IGNORE linkpool(object) SELECT source FROM arrows")
db.execute("INSERT IGNORE linkpool(object) SELECT target FROM arrows")


import syslog
syslog.syslog( syslog.LOG_INFO, "Migrated arrows information into linkpool" )
