#!/usr/bin/env python

import smtplib
import tornado.database
import json
import os
import os.path
import tornado.template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")
template_loader = tornado.template.Loader( os.path.join(os.path.dirname(__file__),'views') )
email_template = template_loader.load('email.html')


from_email = 'asdfasdfasdf@askgraph.com'
to_emails = ['sleepdev@gmail.com']

msg = MIMEText( email_template.generate(message='Message'), 'html' )
msg['Subject'] = 'Subject'
msg['From'] = from_email
msg['To'] = ', '.join(to_emails)

db.execute('INSERT INTO smtp_outgoing(mailfrom,rcpttos,data) VALUES(%s,%s,%s)', from_email, json.dumps(to_emails), msg.as_string())
