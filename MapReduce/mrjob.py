#!/usr/bin/env python

import csv
import sys
import json
argv = sys.argv
while not argv[0].endswith("mrjob.py"):
    argv = argv[1:]

import tornado.database
db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")


if len(argv)>=4 and argv[1] == "start":
    config = {}
    for a in argv[4:]:
        k,v = a.split("=",1)
        config[k] = v
    config = json.dumps(config)
    count = db.get("SELECT count(*) FROM mr_dataset WHERE dataset_name=%s", argv[2])['count(*)'] or 0
    db.execute("INSERT mr_workflow(workflow_route,workflow_value,workflow_config) " +
               "SELECT %s,dataset_value,%s FROM mr_dataset WHERE dataset_name=%s", argv[3], config, argv[2])
    print "Moved %d rows from %s dataset into %s workflow" % (count, argv[2], argv[3])


elif len(argv)==3 and argv[1] == "clear":
    count = db.get("SELECT count(*) FROM mr_workflow WHERE workflow_route=%s", argv[2])['count(*)'] or 0
    db.execute("DELETE FROM mr_workflow WHERE workflow_route=%s", argv[2])
    print "Clear %d tasks from workflow %s" % (count,argv[2])
  

elif len(argv)==3 and argv[1] == "status":
    count = db.get("SELECT count(*) FROM mr_workflow WHERE workflow_route=%s", argv[2])['count(*)'] or 0
    print "%d tasks open for workflow %s" % (count,argv[2])


elif len(argv)==2 and argv[1] == "list":
    for entry in db.query("SELECT * FROM mr_workflow GROUP BY workflow_route"):
        print entry["workflow_route"]


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
