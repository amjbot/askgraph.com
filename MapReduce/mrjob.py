#!/usr/bin/env python

import csv
import sys
import json
argv = sys.argv
while not argv[0].endswith("mrjob.py"):
    argv = argv[1:]

import time
import tornado.database
db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")


if len(argv)>=4 and argv[1] == "start":
    config = {}
    for a in argv[4:]:
        k,v = a.split("=",1)
        config[k] = v
    output = config.pop('output','mr_workflow_task_'+repr(time.time()))
    config = json.dumps(config)
    count = db.get("SELECT count(*) FROM mr_dataset WHERE dataset_name=%s", argv[2])['count(*)'] or 0
    db.execute("INSERT mr_workflow(workflow_route,workflow_output,workflow_value,workflow_config) " +
               "SELECT %s,%s,dataset_value,%s FROM mr_dataset WHERE dataset_name=%s", argv[3], output, config, argv[2])
    print "Moved %d rows from %s dataset into %s workflow with output into %s" % (count, argv[2], argv[3], output)


elif len(argv)==3 and argv[1] == "clear":
    count = db.get("SELECT count(*) FROM mr_workflow WHERE workflow_output=%s", argv[2])['count(*)'] or 0
    db.execute("DELETE FROM mr_workflow WHERE workflow_output=%s", argv[2])
    print "Clear %d tasks from workflow %s" % (count,argv[2])
  

elif len(argv)==3 and argv[1] == "status":
    count = db.get("SELECT count(*) FROM mr_workflow WHERE workflow_output=%s", argv[2])['count(*)'] or 0
    print "%d tasks open for workflow %s" % (count,argv[2])


elif len(argv)==2 and argv[1] == "list":
    for entry in db.query("SELECT * FROM mr_workflow GROUP BY workflow_output"):
        print entry["workflow_output"]


else:
    print "Usage: mrdata.py action [args]"
    print "Actions:"
    print "   start - Start a new MapReduce job"
    print "   clear - Remove items from a MapReduce job queue"
    print "   status - Show status of a MapReduce job"
    print "   list - List running MapReduce jobs"
