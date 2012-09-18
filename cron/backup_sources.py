#!/usr/bin/env python

import boto
import subprocess
import os
from boto.s3.key import Key
import time


subprocess.call("cd /home/ubuntu; tar -czf .backup.git.tar.gz askgraph.com", shell=True)


c = boto.connect_s3("AKIAJ2FGCCGFY3JR32MQ","3nyS22uEb3oQoGvXIq8eT+ceDqONUUbRE8zEYbhF")
b = c.get_bucket('askgraph',validate=False)


if True:
    k = Key(b)
    k.key = "backups/daily.git.tar.gz"
    k.set_contents_from_filename("/home/ubuntu/.backup.git.tar.gz")
if time.gmtime().tm_mday % 7 == 1:
    k = Key(b)
    k.key = "backups/weekly.git.tar.gz"
    k.set_contents_from_filename("/home/ubuntu/.backup.git.tar.gz")
if time.gmtime().tm_mday == 2:
    k = Key(b)
    k.key = "backups/monthly.git.tar.gz"
    k.set_contents_from_filename("/home/ubuntu/.backup.git.tar.gz")

os.remove("/home/ubuntu/.backup.git.tar.gz")

import syslog
syslog.syslog(syslog.LOG_INFO,"created backup of database")
