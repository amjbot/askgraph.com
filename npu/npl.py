#!/usr/bin/env python


import json
import tornado.database
import sys


db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")


for f in sys.argv[1:]:
    assert f.endswith(".npl")
    language = f.rsplit(".",1)[0].split("/")[-1]
    db.execute("DELETE FROM language WHERE language=%s", language)
    for line in file(f):
        if line.strip()=="":
            continue
        symbol,require,effects = json.loads(line)
        db.execute("INSERT INTO language(language,symbol,requires,effects) VALUES(%s,%s,%s,%s)",
            language,symbol,json.dumps(require),json.dumps(effects))


