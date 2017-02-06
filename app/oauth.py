#!fp_env/bin/python
from apiclient import discovery
from oauth2client import client
from oauth2client.client import Flow
from oauth2client.client import flow_from_clientsecrets
from flask import current_app, url_for, request, redirect, session
import httplib2
import flask


class GoogleLogin():

    def __init__(self):
        self.flow = client.flow_from_clientsecrets(
            'client_secrets.json',
            scope='https://www.googleapis.com/auth/userinfo.email',
            redirect_uri='http://localhost:5000/oauth2callback')

    def step1(self):
        self.auth_uri = self.flow.step1_get_authorize_url()
        return flask.redirect(self.auth_uri)

    def step2(self):
        self.auth_code = flask.request.args.get('code')
        self.credentials = self.flow.step2_exchange(self.auth_code)
        flask.session['credentials'] = self.credentials.to_json()

    def userinfo(self):
        self.credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
        self.http_auth = self.credentials.authorize(httplib2.Http())
        self.user_service = discovery.build('oauth2', 'v2', self.http_auth)
        self.userinfor = self.user_service.userinfo().get().execute()
        return self.userinfor
