import json
from flask import request, _request_ctx_stack, Flask, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen

app = Flask(__name__)

AUTH0_DOMAIN = 'coffeeshop01.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee'


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def get_token_auth_header():
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
            }, 401)
    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "bearer".'
            }, 401)
    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
            }, 401)
    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
            }, 401)
    token = parts[1]
    return token
  

def check_permissions(permission, payload):
    raise Exception('Not Implemented')


def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed'
        }, 401)
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN +'/'
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code':'token_expried',
                'description': 'token_expried'
                }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code':'invalid_claims',
                'description': 'Incorrect claims, Please check the audience and issuer.'
                }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
                }, 400)
    raise AuthError({
                'code':'invalid_header',
                'description': 'Unable to find the appropriate key.'
                }, 400)

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                check_permissions(permission, payload)
                return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator

@app.route('/headers')
@requires_auth
def headers(payload):
    print(payload)
    return 'Access Granted'