import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from src.auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)
db_drop_and_create_all()

## ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    drink_info = Drink.query.orderby(Drink.id).all()

    if len(drink_info)==0:
        abort(404)

    drinks = [drink.short() for drink in drink_info]

    return jsonify({
        'success': True,
        'drinks': drinks
    })
    
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drink_info = Drink.query.orderby(Drink.id).all()

    if len(drink_info)==0:
        abort(404)
    
    drinks = [drink.long() for drink in drink_info]

    return jsonify({
        'success':True,
        'drinks': drinks
    })

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    body = request.get_json()
    new_drink = Drink(title = body['title'], recipe = """{}""".format(body['recipe']))
    new_drink.insert()
    new_drink.recipe = body['recipe']
    return jsonify({
        'success': True,
        'drinks': Drink.long(new_drink)
    })

@app.route('/drink/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    body = request.get_json()
    if not body:
        abort(400)
    
    drink_update = Drink.query.filter(Drink.id == id).one_or_none()

    update_title = body.get('title', None)
    update_recipe = body.get('recipe', None)

    if update_title:
        drink_update.title = body['title']

    if update_recipe:
        drink_update.recipe = """"{}""".format(body['recipe'])

    drink_update.update()

    return jsonify({
        'sucess': True,
        'drinks': [Drink.long(drink_update)]
    })

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    drink_info = Drink.query.filter(Drink.id==id).one_or_none()

    if Drink is None:
        abort(404)

    try:
        drink_info.delete()
        return jsonify({
            "success": True,
            "delete":id
        })
    except:
        abort(422)

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
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
        }), error.status_code
