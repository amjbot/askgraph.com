#!/usr/bin/env python

import tornado.database

db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")

for input in db.query("SELECT * FROM noisebot_input"):
    print input.source, input.route
