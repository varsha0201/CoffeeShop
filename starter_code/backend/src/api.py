import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)
# app = Flask(__name__)
# cors = CORS(app, resources={r"/drinks/*": {"origins": "*"}})
# CORS(app)
# setup_db(app)

#db_drop_and_create_all()

# def options (self):
#     return {'Allow' : 'PUT' }, 200, \
#     { 'Access-Control-Allow-Origin': '*', \
#       'Access-Control-Allow-Methods' : 'PUT,GET' }

    
## ROUTES
@app.route('/drinks', methods=['GET','POST'])
def get_drinks():
    drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in drinks]

    return jsonify({
            'success': True,
            'drinks': formatted_drinks
            })
    
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()
    formatted_drinks = [drink.long() for drink in drinks]
    print(formatted_drinks)
    return jsonify({
            'success': True,
            'drinks': formatted_drinks
            })

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
        body = request.get_json(force=True)
        title = body.get('title')
        recipe = str(json.dumps(body.get('recipe')))
        new_drink = Drink(title=title, recipe=recipe)
        new_drink.insert()
        drinks = []
        drinks.append(new_drink.long())
        return jsonify({
                'success': True,
                'drinks': drinks
                })

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    drink = Drink.query.get(id)
    print(drink)
    if drink is None:
            abort(404)
    else:
            body = request.get_json()
            title = body.get('title', None)
            recipe = json.loads(json.dumps(body.get('recipe', None)))

            if title is not None and title != '':
                    drink.title = title
            if recipe is not None and recipe != '':
                    drink.recipe = str(recipe)
                    drink.update()
                    drinks = []
                    drinks.append(drink.long())

            return jsonify({
                    'success': True,
                    'drinks': drinks
                    })


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    drink = Drink.query.get(id)

    if drink is None:
        abort(404)
    else:
        drink.delete()

        return jsonify({
            'success': True,
            'delete': id
            })

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
        }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "resource not found"
        }), 400

@app.errorhandler(AuthError)
def handle_auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error.code
        }), error.status_code
