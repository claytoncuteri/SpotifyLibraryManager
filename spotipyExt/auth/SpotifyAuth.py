import json
import os
from .. import spotipyExt

CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_secret.json')
DEFAULT_SCOPE = 'user-library-read playlist-read-private'

def get_uid(client_secret_file = CLIENT_SECRETS_FILE):
    with open(client_secret_file, 'r') as fid:
        credz = json.load(fid)
    return credz['userconfig']['uid']

def get_authenticated_service(client_secret_file=CLIENT_SECRETS_FILE, scope=DEFAULT_SCOPE):
    return spotipyExt.initializeSpotifyToken(scope, get_uid(client_secret_file))