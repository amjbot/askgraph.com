#!/usr/bin/env python


import smtpd
import asyncore
import tornado.database
import sys
import json


db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")


smtpd.DEBUGSTREAM = sys.stderr


class SMTPServer(smtpd.SMTPServer):
    
    def process_message(self, peer, mailfrom, rcpttos, data):
        peer = json.dumps(peer)
        rcpttos = json.dumps(rcpttos)
        try:
            db.execute("INSERT INTO smtp_incoming(peer,mailfrom,rcpttos,data) VALUES(%s,%s,%s,%s)",
                peer, mailfrom, rcpttos, data)
        except:
            import traceback
            traceback.print_exc()


server = SMTPServer(('0.0.0.0', 25), None)
asyncore.loop()
