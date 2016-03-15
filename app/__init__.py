import os
import sys

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail

app = Flask(__name__)
app.config.from_object('config')
try:
    app.config.from_envvar('PASSPORT_SETTINGS')
except:
    pass

db = SQLAlchemy(app)
mail = Mail(app)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

from app.users.views import mod as usersModule
app.register_blueprint(usersModule)
