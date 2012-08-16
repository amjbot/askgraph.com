#!/usr/bin/env python

import tornado.database
import sys
import glob

db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")

for filename in glob.glob("sources/*.txt"):
    route = filename.rsplit('.',1)[0].split('/')[-1]
    for line in open(filename):
        line = line.strip()
        if line=="":
            continue
        db.execute("INSERT IGNORE noisebot_input(source,route) VALUES(%s,%s)", line, route)
