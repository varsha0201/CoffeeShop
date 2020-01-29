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
    
    if 'Authorization' not in request.headers:
        raise AuthError({
                'code': 'invalid_header',
                'description': 'No Authorization in header.'
            }, 401)

    auth_header = request.headers['Authorization']
    header_parts = auth_header.split(' ')

    if len(header_parts) != 2:
        raise AuthError({
                'code': 'invalid_header',
                'description': 'Authorization malformed.'
            }, 401)
    elif header_parts[0] != 'Bearer':
        raise AuthError({
                'code': 'invalid_header',
                'description': 'Authorization malformed.'
            }, 401)

    return header_parts[1]
  
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
                'code': 'bad_request',
                'description': 'No permissions in payload.'
            }, 400)
    if permission not in payload['permissions']:
        raise AuthError({
                'code': 'forbidden',
                'description': 'User does not have required permission.'
            }, 403)

    return True

def verify_decode_jwt(token):
    # GET THE PUBLIC KEY FROM AUTH0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # GET THE DATA IN THE TOKEN HEADER
    unverified_header = jwt.get_unverified_header(token)

    # CHOOSE OUR KEY
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
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
    
    # verify token
    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
                return f(payload, *args, **kwargs)
            except AuthError as e:
                print(e.error)
                abort(e.status_code)

        return wrapper
    return requires_auth_decorator