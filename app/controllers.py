import tornado.web
import tornado.database
import md5
import random
import string
import smtplib
from email.mime.text import MIMEText

db = tornado.database.Connection(host="localhost",user="root",database="root",password="root")

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time 
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago"

class BaseHandler( tornado.web.RequestHandler ):
    def get_current_user( self ):
        email = self.get_secure_cookie("user.email")
        if email:
            return db.get("SELECT * FROM user WHERE email=%s", email)

class index( BaseHandler ):
    def get( self ):
        self.render( "index.html", pretty_date=pretty_date )

class create( BaseHandler ):
    def get( self ):
        self.render( "create.html" )

class worlds( BaseHandler ):
    def get( self ):
        self.render( "worlds.html" )

class world_identities( BaseHandler ):
    def get( self, world ):
        self.render( "world_identities.html", world=world )

class world_player( BaseHandler ):
    def get( self, world, player ):
        self.render( "world_player.html", world=world, player=player )

class confirm( BaseHandler ):
    def get( self ):
        email = self.get_argument("email","")
        confirm = self.get_argument("confirm","")
        user = db.get("SELECT * FROM user WHERE email=%s and name=%s", email, ' '+confirm)
        self.render("confirm.html", email=email, confirm=confirm, user=user)
    def post( self ):
        email = self.get_argument("email","")
        confirm = self.get_argument("confirm","")
        name = self.get_argument("name","")
        db.execute("UPDATE user SET name=%s WHERE email=%s AND name=%s", name, email, ' '+confirm)
        self.redirect("/authenticate?alert=confirmation-success")


confirm_msg = """
   Please confirm your askgraph.com identity by clicking this link:

   http://www.askgraph.com/confirm?email={email}&confirm={confirm}
"""
class authenticate( BaseHandler ):
    def get( self ):
        self.render( "authenticate.html" )
    def post( self ):
        next = self.get_argument("next","/")
        email = self.get_argument("email","")
        password = self.get_argument("password","")
        m = md5.new()
        m.update(email)
        m.update(password)
        passhash = m.hexdigest()
        user = db.get("SELECT * FROM user WHERE email=%s", email)
        if not user:
	    chars = string.ascii_uppercase + string.digits
            confirm = ''.join(random.choice(chars) for x in range(10))
            msg = MIMEText(confirm_msg.format(email=email, confirm=confirm))
            msg['Subject'] = 'Please confirm your askgraph.com identity'
            msg['From'] = "admin@askgraph.com"
            msg['To'] = email
            s = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com',25)
            s.starttls()
            s.login("AKIAIO5DMTF3VIANFM3A", "AtBSmTPASAF6JOp8O7H1HD77u8KxMO0u6ouSLl2XGuqi")
            s.sendmail("admin@askgraph.com", [email], msg.as_string())
            s.quit()
            db.execute("INSERT user (email,passhash,name) VALUES (%s,%s,%s)", email, passhash, ' '+confirm)
            self.redirect("/authenticate?error=pending&next="+next)
        elif user.name.startswith(" "):
            self.redirect("/authenticate?error=pending-confirmation&next="+next)
        elif user.passhash != passhash:
            self.redirect("/authenticate?error=invalid-identity&next="+next)
        else:
            self.set_secure_cookie("user.email", email)
            self.redirect(next)
