import tornado.database
db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")

i = 0
for i,item in enumerate(db.query("select noisebot_output.*, link_firehose.state from noisebot_output left join link_firehose on "
                    "noisebot_output.id=link_firehose.id where state IS NULL limit 100")):
    db.execute("INSERT link_firehose(id,state) VALUES(%s,'open')", item.id)

qbert.insert()
print "populate link firehose with %d new links" % i
