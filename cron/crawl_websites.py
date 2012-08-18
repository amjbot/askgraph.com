#!/usr/bin/env python

import daemon
daemon.singleton("crawl_websites.pid")

import noisebot
import tornado.database
import json
db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")

i = -1
for i,task in enumerate(db.query("SELECT * FROM mr_workflow WHERE workflow_route='crawl' ORDER BY RAND() LIMIT 1")):
    db.execute("DELETE FROM mr_workflow WHERE id=%s", task.id)
    output = task.workflow_output
    value = json.loads(task.workflow_value)
    config = json.loads(task.workflow_config)
    for v in value.values():
        if v.startswith("http://") or v.startswith("https://"):
            results = noisebot.crawl( v, **config )
            for doc in results:
                db.execute("INSERT mr_dataset(dataset_name,dataset_value) VALUES(%s,%s)", output, json.dumps({"data": doc}))


import syslog
syslog.syslog( syslog.LOG_INFO, "crawled %d website" % (i+1) )
