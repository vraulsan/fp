#!fp_env/bin/python
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import basedir
import json
import httplib2
from apiclient import discovery
from oauth2client import client
import urllib
from .oauth import GoogleLogin
from flask_bootstrap import Bootstrap




app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
googler = GoogleLogin()
Bootstrap(app)

from app import views, models, oauth, Bootstrap

