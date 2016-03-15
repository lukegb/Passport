import os, os.path
_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

ADMINS = set(['sysops@spongepowered.org'])
SECRET_KEY = 'please change me'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'tmp', 'app.db')
DATABASE_CONNECT_OPTIONS = {}
SQLALCHEMY_TRACK_MODIFICATIONS = False

THREADS_PER_PAGE = 8

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'please change me'

JWT_ENCODE_ALGO = 'ES512'
JWT_DECODE_ALGOS = [JWT_ENCODE_ALGO]
JWT_SECRET_KEY = '-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIBB8owU+Aqx+wfYv24nBuRX4+9jon7qI6cS/uVOiAFKNoAoGCCqGSM49\nAwEHoUQDQgAEN1lGIZ/WZ+bvnDaIVwwsMBAJOAsSbnWj7AGUFFG3I/pxN29lfcCk\npYKX/1Wrbl4LfRab4mSzhqXo1BNeAn/+WQ==\n-----END EC PRIVATE KEY-----\n'
JWT_PUBLIC_KEY = '-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEN1lGIZ/WZ+bvnDaIVwwsMBAJOAsS\nbnWj7AGUFFG3I/pxN29lfcCkpYKX/1Wrbl4LfRab4mSzhqXo1BNeAn/+WQ==\n-----END PUBLIC KEY-----\n'
JWT_DOMAIN = None
JWT_SECURE = False

SERVER_NAME = 'localhost:5000'

MAIL_DEFAULT_SENDER = 'admin@spongepowered.org'
MAIL_PORT = 1025

RESERVE_NAME_SECRET = '1N4hypg0Xu2v5N861qE5zfuw2QZDBI46'
