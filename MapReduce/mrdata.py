#!/usr/bin/env python

import csv
import sys
import json
argv = sys.argv
while not argv[0].endswith("mrdata.py"):
    argv = argv[1:]

import tornado.database
db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")


if len(argv)==3 and argv[1] == "load" and (argv[2].endswith('.csv') or argv[2].endswith('.txt')):
    dataset = argv[2].split('/')[-1].rsplit('.',1)[0]
    format = argv[2].rsplit('.',1)[1]
    exists = db.get("SELECT * FROM mr_dataset WHERE dataset_name=%s LIMIT 1", dataset)
    if exists:
        db.execute("DELETE FROM mr_dataset WHERE dataset_name=%s", dataset)
    if format=="csv":
        i = -1
        for i,entry in enumerate(csv.DictReader(open(argv[2]))):
            db.execute("INSERT mr_dataset(dataset_name,dataset_value) VALUES(%s,%s)", dataset, json.dumps(entry))
        print "Created dataset %s with %d rows" % (dataset,i+1)
    elif format=="txt":
        i = -1
        for i,entry in enumerate(open(argv[2])):
            if entry.strip()=="": continue
            db.execute("INSERT mr_dataset(dataset_name,dataset_value) VALUES(%s,%s)", dataset, json.dumps({"data": entry}))
        print "Created dataset %s with %d rows" % (dataset,i+1)
    else:
        assert False


elif len(argv)==3 and argv[1] == "remove":
    count = db.get("SELECT count(*) FROM mr_dataset WHERE dataset_name=%s", argv[2])['count(*)']
    db.execute("DELETE FROM mr_dataset WHERE dataset_name=%s", argv[2])
    print "Removed %s dataset with %d rows" % (argv[2], count or 0)


elif len(argv)==3 and argv[1] == "show":
    for entry in db.query("SELECT * FROM mr_dataset WHERE dataset_name=%s", argv[2]):
        print entry['dataset_value']


elif len(argv)==2 and argv[1] == "list":
    for entry in db.query("SELECT * FROM mr_dataset GROUP BY dataset_name"):
        print entry["dataset_name"]


elif len(argv)==4 and argv[1] == "move":
    count = db.get("SELECT count(*) FROM mr_dataset WHERE dataset_name=%s", argv[2])['count(*)']
    db.execute("UPDATE mr_dataset SET dataset_name=%s WHERE dataset_name=%s", argv[3], argv[2])
    print "Renamed dataset %s with %d rows to %s" % (argv[2], count, argv[3])


elif len(argv)==4 and argv[1] == "copy":
    count = db.get("SELECT count(*) FROM mr_dataset WHERE dataset_name=%s", argv[2])['count(*)']
    db.execute("INSERT INTO mr_dataset(dataset_name,dataset_value) SELECT %s,dataset_value FROM mr_dataset WHERE dataset_name=%s", argv[3], argv[2])
    print "Copied dataset %s with %d rows to %s" % (argv[2], count, argv[3])


else:
    print "Usage: mrdata.py action [args]"
    print "Actions:"
    print "   list - list available datasets"
    print "   load - load a new dataset from csv"
    print "   show - show a dataset in csv format"
    print "   remove - remove a dataset from the database"
    print "   move - move a dataset to a new location"
    print "   copy - copy a dataset to a new location"
    print "   describe - describe the structure of a dataset"
