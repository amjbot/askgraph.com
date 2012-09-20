#!/usr/bin/env python


import sys
import tornado.database


db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")


def push( ticket_id ):
    request = db.get("SELECT * FROM requests WHERE id=%s", ticket_id)
    thread = db.query("SELECT * FROM request_responses WHERE request_id=%s ORDER BY ts asc", ticket_id)
if len(sys.argv)==3 and sys.argv[1]=='push': 
    ticket_id = int(sys.argv[2])
    push( ticket_id=ticket_id )


def edit( ticket_id ):
    request = db.get("SELECT * FROM requests WHERE id=%s", ticket_id)
    thread = db.query("SELECT * FROM request_responses WHERE request_id=%s ORDER BY ts asc", ticket_id)
    print 'Not implemented'
if len(sys.argv)==3 and sys.argv[1]=='edit': 
    ticket_id = int(sys.argv[2])
    edit( ticket_id=ticket_id )


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


'''
CREATE TABLE IF NOT EXISTS request_responses (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    contact VARBINARY(500) NOT NULL,
    comment TEXT NOT NULL,
    context TEXT NOT NULL,
    ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY(request_id)
);
'''    
