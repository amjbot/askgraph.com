#!/usr/bin/env python


import smtplib
import tornado.database
import json
import os
import os.path


db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")


def send( from_email, to_emails, data ):
    s = smtplib.SMTP()
    s.connect('email-smtp.us-east-1.amazonaws.com',25)
    s.starttls()
    s.login('AKIAJI6B5SDZHOPEYZSA','Ahst9zkrH0T2ma+JlCnKN1NFWKFWJWJWBpjTfIxqJY5O')
    s.sendmail(from_email,to_emails,data)
    s.quit()


for outgoing in db.query("SELECT * FROM smtp_outgoing ORDER BY ts ASC LIMIT 20"):
    outgoing.rcpttos = json.loads(outgoing.rcpttos)
    send( from_email=outgoing.mailfrom, to_emails=outgoing.rcpttos, data=outgoing.data )
    db.execute("DELETE FROM smtp_outgoing WHERE id=%s", outgoing.id)
