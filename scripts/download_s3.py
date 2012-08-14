#!/usr/bin/env python

import boto
import glob
import os
import os.path
from boto.s3.key import Key
import subprocess
import sys

c = boto.connect_s3("AKIAJ2FGCCGFY3JR32MQ","3nyS22uEb3oQoGvXIq8eT+ceDqONUUbRE8zEYbhF")
b = c.get_bucket('askgraph',validate=False)
k = Key(b)
filename = "backups/daily.sql.tar.gz" if sys.argv[-1].endswith("download_s3.py") else sys.argv[-1]
k.key = filename
k.get_contents_to_filename(filename.split("/")[-1])
