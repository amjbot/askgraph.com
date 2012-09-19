#!/usr/bin/env python


import smtplib
import tornado.template
import os
import os.path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


template_loader = tornado.template.Loader( os.path.join(os.path.dirname(__file__),'views') )
email_template = template_loader.load('email.html')


def send( from_email, to_email, subject, message ):
    s = smtplib.SMTP()
    s.connect('email-smtp.us-east-1.amazonaws.com',25)
    s.starttls()
    s.login('AKIAJI6B5SDZHOPEYZSA','Ahst9zkrH0T2ma+JlCnKN1NFWKFWJWJWBpjTfIxqJY5O')
    msg = MIMEText( email_template.generate(message=message), 'html' )
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    s.sendmail(from_email,[to_email], msg.as_string() )
    s.quit()


send( from_email='asdfasdfasdfasdf@askgraph.com', to_email='sleepdev@gmail.com', subject='Subject', message='Message' )
