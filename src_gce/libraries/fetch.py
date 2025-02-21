from httplib2 import Http
from oauth2client.client import GoogleCredentials
from json import dumps

def _get_http_authorized():
    credentials = GoogleCredentials.get_application_default()
    http_auth = credentials.authorize(Http())
    return http_auth

def post_as_admin(url, data):

    http_auth = _get_http_authorized()

    return http_auth.request(
        uri=url,
        method="POST",
        headers={'Content-Type': 'application/json; charset=UTF-8'},
        body=dumps(data))


def get_as_admin(url):
    http_auth = _get_http_authorized()

    return http_auth.request(
        uri=url,
        method="GET",
        headers={'Content-Type': 'application/json; charset=UTF-8'})
