#!/usr/bin/env python


import sys
import tornado.database
import json
import random
import string
import tempfile
import subprocess


db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")


def push( ticket_id ):
    request = db.get("SELECT * FROM requests WHERE id=%s", ticket_id)
    thread = db.query("SELECT * FROM request_responses WHERE request_id=%s ORDER BY ts asc", ticket_id)
if len(sys.argv)==3 and sys.argv[1]=='push': 
    ticket_id = int(sys.argv[2])
    push( ticket_id = ticket_id )


def edit( ticket_id ):
    request = db.get("SELECT * FROM requests WHERE id=%s", ticket_id)
    thread = db.query("SELECT * FROM request_responses WHERE request_id=%s ORDER BY ts asc", ticket_id)
    if len(thread)==0 or thread[-1].contact==request.contact:
        contact = (db.get("SELECT contact FROM request_responses WHERE request_id=%s AND contact LIKE '%%@askgraph.com'",request.id) \
            or {'contact': ''.join(random.choice(string.letters + string.digits) for x in range(16)) })["contact"]
        db.execute("INSERT INTO request_responses(request_id,contact,comment,context) VALUES(%s,%s,%s,%s)",
            request.id, contact, '', json.dumps({}) )
    thread = db.query("SELECT * FROM request_responses WHERE request_id=%s ORDER BY ts asc", ticket_id)
    f = tempfile.NamedTemporaryFile(suffix='_edit_message', mode='w+t', delete=False)
    message_separator = '\n===============================\n\n'
    for t in [request]+thread[:-1]:
        t.context = json.loads(t.context)
        f.write( 'From ' + t.contact + '\n' )
        for k in t.context:
            f.write(k + ': ' + t.context[k] + '\n')
        f.write( 'Date: ' + t.ts.isoformat() + '\n' )
        f.write( '\n' )
        f.write( t.get("request","") or t.get('comment','') )
        f.write( message_separator )
    t = db.get("SELECT * FROM request_responses WHERE request_id=%s ORDER BY ts desc LIMIT 1", ticket_id)
    f.write( t.comment )
    n = f.name
    f.close()
    subprocess.call(['nano', n])
    with open(n) as f:
        comment = f.read().split( message_separator )[-1]
        db.execute("UPDATE request_responses SET comment=%s WHERE id=%s", comment, t.id)
if len(sys.argv)==3 and sys.argv[1]=='edit': 
    ticket_id = int(sys.argv[2])
    edit( ticket_id = ticket_id )


if len(sys.argv)==2 and sys.argv[1]=='edit': 
    requests = db.query("SELECT * FROM requests ORDER BY ts ASC LIMIT 10")
    print 'Choose a document to edit.'
    for r in requests:
        print r.id, '>', r.request[:100]
    d = None
    while d is None:
        s = raw_input('# > ')
        try:
            d = [ d for d in requests if d.id==int(s) ][0]
        except:
            print 'Document id not found, try again.'
    edit( ticket_id = d.id )


