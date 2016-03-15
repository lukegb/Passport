from flask import Blueprint, request, render_template, flash, g, redirect, url_for, current_app, make_response
from werkzeug import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import jwt

from app import db, mail
from app.users.models import User
from app.users.utils import is_safe_url
from app.users.decorators import requires_login, requires_reserve_name_secret
from app.users.forms import LoginForm

mod = Blueprint('users', __name__, url_prefix='/users')

@mod.before_request
def before_request():
    g.user = None

    spauth = request.cookies.get('spauth', None)
    if not spauth:
        return

    try:
        innards = jwt.decode(spauth, current_app.config['JWT_PUBLIC_KEY'], algorithms=current_app.config['JWT_DECODE_ALGOS'], audience='urn:spongepowered', issuer='urn:spongepowered:passport')
        g.user = User.query.get(innards['user']['id'])
    except:
        pass

@mod.before_request
def before_request_banned():
    if g.user is not None and g.user.banned:
        now = datetime.utcnow()
        if g.user.banned_until and now > g.user.banned_until:
            # time for a reprieve, it seems
            g.user.staff_notes += "\n\nSystem unbanned user at {} UTC as ban time expired.".format(now.strftime('%Y-%m-%d %H:%M:%S'))
            if g.user.ban_reason:
                g.user.staff_notes += "\nThey had been banned for: {}".format(g.user.ban_reason)
            else:
                g.user.staff_notes += "\nNo ban reason was provided."

            g.user.banned = False
            g.user.banned_until = None
            g.user.ban_reason = ''
            db.session.add(g.user)
            db.session.commit()
        else:
            return make_response(render_template('users/banned.html', user=g.user), 403)

@mod.before_request
def before_request_inactive():
    if g.user is not None and not g.user.active:
        if request.path != url_for('users.activate_account'):
            return redirect(url_for('users.activate_account'))

@mod.after_request
def after_request(response):
    if g.user is None and request.cookies.get('spauth', None) is not None:
        response.set_cookie('spauth', '', expires=0, secure=current_app.config['JWT_SECURE'], httponly=True, domain=current_app.config['JWT_DOMAIN'])
        response = clear_forums_cookies(response)
    return response


def check_user(resp, user):
    g.user = user

    resp_handlers = [before_request_banned, before_request_inactive]
    for resp_handler in resp_handlers:
        overresp = resp_handler()
        if overresp is not None:
            return overresp

    return resp


def clear_forums_cookies(resp):
    resp.set_cookie('_t', '', httponly=True, secure=False, expires=0, domain='forums.spongepowered.org')
    resp.set_cookie('_t', '', httponly=True, secure=False, expires=0, domain='.spongepowered.org')
    return resp


def set_jwt(resp, user):
    g.user = user
    now = datetime.utcnow()
    jwtdict = {
        'exp': now + timedelta(days=1),
        'nbf': now,
        'iat': now,
        'iss': 'urn:spongepowered:passport',
        'aud': 'urn:spongepowered',
        'user': user.to_json(),
    }
    jwtstr = jwt.encode(jwtdict, current_app.config['JWT_SECRET_KEY'], algorithm=current_app.config['JWT_ENCODE_ALGO'])
    resp.set_cookie('spauth', jwtstr, secure=current_app.config['JWT_SECURE'], httponly=True, domain=current_app.config['JWT_DOMAIN'], )
    return clear_forums_cookies(resp)


@mod.route('/login/', methods=['GET', 'POST'])
def login():
    next_loc = request.form.get('next', request.args.get('next', None))
    if next_loc is None or not is_safe_url(next_loc):
        next_loc = 'https://forums.spongepowered.org'

    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            return set_jwt(check_user(redirect(next_loc), user), user)

        if not user:
            form.username.errors.append("There don't seem to be any users by that username.")
        else:
            form.password.errors.append("This password is incorrect.")

    return render_template("users/login.html", form=form, next=next_loc)


@mod.route('/test/', methods=['GET'])
@requires_login
def test():
    import json
    return render_template("users/test.html", user=json.dumps(g.user.to_json(), sort_keys=True, indent=4))


@mod.route('/logout/', methods=['GET'])
def logout():
    g.user = None
    # after_request will take care of it
    return redirect(url_for("users.login"))


@mod.route('/activate/', methods=['GET', 'POST'])
def activate_account():
    if not g.user:
        return redirect(url_for('users.login'))
    if g.user.active:
        return redirect('https://forums.spongepowered.org')

    if request.method == 'POST' and 'resend' in request.form:
        msg = g.user.make_activation_email()
        mail.send(msg)

    data = {}
    if 'key' in request.args:
        jwtstr = request.args.get('key')
        broken = False
        try:
            jwtcontent = jwt.decode(jwtstr, current_app.config['JWT_PUBLIC_KEY'], algorithms=current_app.config['JWT_DECODE_ALGOS'], audience='urn:spongepowered:passport', issuer='urn:spongepowered:passport')
        except:
            broken = True
            data['bad_token'] = True
        if not broken and jwtcontent.get('user_id', None) != g.user.id:
            data['not_your_user'] = True
            broken = True
        if not broken:
            u = g.user
            u.active = True
            db.session.add(u)
            db.session.commit()
            return redirect('https://forums.spongepowered.org')

    return render_template("users/activate.html", **data)


@mod.route('/reservation/<username>/', methods=['POST', 'DELETE', 'GET'])
@requires_reserve_name_secret
def reserve_name(username):
    appname = request.args.get('appname', None)
    if request.method in ['POST', 'DELETE'] and not appname:
        return make_response('No "appname".', 400)

    if request.method == 'POST':
        u = User()
        u.username = username
        u.name = appname
        u.password = '!!!'
        u.email = ''
        u.active = False
        u.is_reserved_name = True
        try:
            db.session.add(u)
            db.session.commit()
        except Exception as ex:
            print(ex)
            return make_response('Conflict :(', 409)

        return make_response('OK!', 201)
    elif request.method == 'DELETE':
        u = User.query.filter_by(name=appname, username=username, is_reserved_name=True).first()
        if u is None:
            return make_response('not valid.', 400)

        db.session.delete(u)
        db.session.commit()
        return make_response('Deleted.', 200)
    elif request.method == 'GET':
        u = User.query.filter_by(username=username, is_reserved_name=True).first()
        if u is None:
            return make_response('Nope.', 404)
        return make_response(u.name, 200)

