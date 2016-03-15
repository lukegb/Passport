from app import db
from app.users import constants as USER
from flask.ext.mail import Message
from flask import current_app, url_for

from datetime import datetime, timedelta
import hashlib
import jwt


class User(db.Model):
    __tablename__ = 'users_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    name = db.Column(db.String(255))
    email = db.Column(db.String(513), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)
    moderator = db.Column(db.Boolean, default=False, nullable=False)
    active_avatar = db.Column(db.Integer, db.ForeignKey('users_useravatar.id'))
    avatars = db.relationship('UserAvatar', backref='user', lazy='dynamic', foreign_keys='UserAvatar.user_id')

    active = db.Column(db.Boolean, default=False, nullable=False)
    banned = db.Column(db.Boolean, default=False, nullable=False)
    banned_until = db.Column(db.DateTime(timezone=True), nullable=True)
    ban_reason = db.Column(db.String(512), nullable=False, default='')

    staff_notes = db.Column(db.Text, nullable=False, default='')

    def to_json(self):
        COLS = ['id', 'username', 'name', 'email', 'admin', 'moderator', 'avatar_url', 'active']
        out = {}
        for k in COLS:
            out[k] = getattr(self, k)
        return out

    @property
    def gravatar_url(self):
        h = hashlib.md5()
        h.update(self.email.encode('utf8'))
        return '//www.gravatar.com/avatar/{}?d=mm&size=32'.format(h.hexdigest())

    @property
    def avatar_url(self):
        if not self.active_avatar:
            return self.gravatar_url
        print(self.active_avatar)

    def make_activation_email(self):
        if self.active:
            return

        now = datetime.utcnow()
        activation_key = jwt.encode({
            'exp': now + timedelta(hours=6),
            'nbf': now,
            'iat': now,
            'aud': 'urn:spongepowered:passport',
            'iss': 'urn:spongepowered:passport',
            'user_id': self.id,
        }, current_app.config['JWT_SECRET_KEY'], algorithm=current_app.config['JWT_ENCODE_ALGO'])

        msg = Message(
            recipients=[self.email],
            subject="SpongePowered Passport: Activate your Account",
            body="""
Hi there, {user.username}!

You're just one step away from activating your account - simply click the link below and you'll be all set up:

{activation_url}

Thanks,
The SpongePowered Team
""".strip().format(user=self, activation_url=url_for('users.activate_account', key=activation_key, _external=True))
        )
        return msg


class UserAvatar(db.Model):
    __tablename__ = 'users_useravatar'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_user.id'))
    local_filename = db.Column(db.String(255), unique=True, nullable=True)
    remote_url = db.Column(db.String(255), unique=True, nullable=True)
