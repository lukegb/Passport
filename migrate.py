import os
_basedir = os.path.abspath(os.path.dirname(__file__))
_dbfile = os.path.join(_basedir, 'tmp', 'app.db')
try:
    os.unlink(_dbfile)
except:
    pass

from app import db
db.create_all()

import datetime
from app.users.models import User
from werkzeug import generate_password_hash
def create_user(username, password, email, name):
    u = User()
    u.username = username
    u.password = generate_password_hash(password)
    u.email = email
    u.name = name
    u.active = True
    return u

lukegb = create_user('lukegb', 'password', 'spongepassport@lukegb.com', 'lukegb\'s name')

banned = create_user('banned', 'password', 'banned@lukegb.com', 'banned')
banned.banned_until = datetime.datetime.utcnow() + datetime.timedelta(days=3650)
banned.banned = True
banned.ban_reason = 'Unsociable folk, ain\'t he?'

bforever = create_user('banned_forever', 'password', 'bforever@lukegb.com', 'banned')
bforever.banned_until = None
bforever.banned = True
bforever.ban_reason = 'Unsociable folk, ain\'t he?'

inactive = create_user('inactive', 'password', 'inactive@lukegb.com', 'inactive')
inactive.active = False

db.session.add(lukegb)
db.session.add(banned)
db.session.add(bforever)
db.session.add(inactive)
db.session.commit()
