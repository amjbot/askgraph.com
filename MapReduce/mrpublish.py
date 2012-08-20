#!/usr/bin/env python


import sys
import json
argv = sys.argv
while not argv[0].endswith("mrpublish.py"):
    argv = argv[1:]

import tornado.database
db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")


if len(argv)==2:
    dataset_name = argv[1]
    dataset = db.query("SELECT * FROM mr_dataset WHERE dataset_name=%s", dataset_name)
    dataset = [ json.loads(v.dataset_value) for v in dataset ]
    if len(dataset)==0:
        print "Could not find any dataset with the name %s" % dataset_name
    else:
        db.execute("DELETE FROM document_headers WHERE dataset=%s", dataset_name)
        db.execute("DELETE FROM documents WHERE dataset=%s", dataset_name)
        keys = set()
        for d in dataset:
            for k in d:
                keys.add(k)
        keys = list(keys)
        db.execute("INSERT document_headers(dataset," + ",".join("col"+str(i) for i in range(len(keys))) +
                   ") VALUES(%s," + ",".join("%s" for i in range(len(keys))) + ")",
                   dataset_name, *keys )
        for d in dataset:
            db.execute("INSERT documents(dataset," + ",".join("col"+str(i) for i in range(len(keys))) +
                   ") VALUES(%s," + ",".join("%s" for i in range(len(keys))) + ")",
                   dataset_name, *(d.get(k,"") for k in keys) )
            
