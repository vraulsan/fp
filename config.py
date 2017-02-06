import os

WTF_CSRF_ENABLED = True
SECRET_KEY = 'kornkid182'

OAUTH_CREDENTIALS = {
        'google': {
            'id': '1085059713125-fnudulnkmcbqvb9e96uaqpv97e1fkloe.apps.googleusercontent.com',
            'secret': 'm7jr-XFHy8ixhIe4vGNQHFv-'
        },
        'twitter': {
            'id': '3RzWQclolxWZIMq5LJqzRZPTl',
            'secret': 'm9TEd58DSEtRrZHpz2EjrV9AhsBRxKMo8m3kuIZj3zLwzwIimt'
        }
    }

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'fpapp.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
POSTS_PER_PAGE = 5
