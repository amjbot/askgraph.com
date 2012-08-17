#!/usr/bin/env python

import csv
import sys
import json
argv = sys.argv
while not argv[0].endswith("mrdata.py"):
    argv = argv[1:]

import tornado.database
db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")


if argv[1] == "load" and len(argv)==3:
    dataset = argv[2].rsplit('.',1)[0]
    exists = db.get("SELECT * FROM mr_dataset WHERE dataset_name=%s LIMIT 1", dataset)
    if exists:
        print "A dataset with that name already exists"
    else:
        i = -1
        for i,entry in enumerate(csv.DictReader(open(argv[2]))):
            db.execute("INSERT mr_dataset(dataset_name,dataset_value) VALUES(%s,%s)", dataset, json.dumps(entry))
        print "Created dataset %s with %d rows" % (dataset,i+1)


elif argv[1] == "rm" and len(argv)==3:
    count = db.get("SELECT count(*) FROM mr_dataset WHERE dataset_name=%s", argv[2])['count(*)']
    db.execute("DELETE FROM mr_dataset WHERE dataset_name=%s", argv[2])
    print "Removed %s dataset with %d rows" % (argv[2], count or 0)


elif argv[1] == "dump" and len(argv)==3:
    for entry in db.query("SELECT * FROM mr_dataset WHERE dataset_name=%s", argv[2]):
        print entry['dataset_value']


elif argv[1] == "list":
    for entry in db.query("SELECT * FROM mr_dataset GROUP BY dataset_name"):
        print entry["dataset_name"]


else:
    print argv
    print "Usage: mrdata.py action [args]"
    print "Actions:"
    print "   list - list available datasets"
    print "   load - load a new dataset from csv"
    print "   dump - dump a dataset to csv"
    print "   move - move a dataset to a new location"
    print "   copy - copy a dataset to a new location"
    print "   describe - describe the structure of a dataset"
