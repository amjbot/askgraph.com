import boto
import subprocess
import os
from boto.s3.key import Key
import time

subprocess.call("mysqldump root -u root -proot > .backup.sql", shell=True)
subprocess.call("tar -czf backup.sql.tar.gz .backup.sql", shell=True)

c = boto.connect_s3("AKIAJ2FGCCGFY3JR32MQ","3nyS22uEb3oQoGvXIq8eT+ceDqONUUbRE8zEYbhF")
b = c.get_bucket('askgraph',validate=False)


if True:
    k = Key(b)
    k.key = "backups/daily.sql.tar.gz"
    k.set_contents_from_filename("backup.sql.tar.gz")
if time.gmtime().tm_mday % 7 == 1:
    k = Key(b)
    k.key = "backups/weekly.sql.tar.gz"
    k.set_contents_from_filename("backup.sql.tar.gz")
if time.gmtime().tm_mday == 2:
    k = Key(b)
    k.key = "backups/monthly.sql.tar.gz"
    k.set_contents_from_filename("backup.sql.tar.gz")

os.remove(".backup.sql")
os.remove("backup.sql.tar.gz")

qbert.insert( delay=60*60*24 )
print "created backup of database"
