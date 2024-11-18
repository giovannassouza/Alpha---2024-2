from flask import Blueprint, url_for, redirect
from . import oauth, db, google
from website.models import *


auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo', token=token)
    resp.raise_for_status()
    user_info = resp.json()
    # do something with the token and profile
    return redirect('/')