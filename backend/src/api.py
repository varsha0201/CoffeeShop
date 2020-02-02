import json
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)
db_drop_and_create_all()


## ROUTES
def get_all_drinks(recipe_format):
    # Get all drinks in database
    all_drinks = Drink.query.order_by(Drink.id).all()
    # Format with different recipe detail level
    if recipe_format.lower() == 'short':
        all_drinks_formatted = [drink.short() for drink in all_drinks]
    elif recipe_format.lower() == 'long':
        all_drinks_formatted = [drink.long() for drink in all_drinks]
        print(all_drinks_formatted)
    else:
        return abort(500, {'message': 'bad formatted function call.\
        recipe_format needs to be "short" or "long".'})

    if len(all_drinks_formatted) == 0:
        abort(404, {'message': 'no drinks found in database.'})
    # Return formatted list of drinks
    return all_drinks_formatted

#----------------------------------------------------------------------------#
# Endpoints
#----------------------------------------------------------------------------#

# TODO DONE implement endpoint GET /drinks
@app.route('/drinks', methods=['GET'])
def drinks():
    drinks = Drink.query.all()
    drinks_formatted = [drinks.short() for drinks in drinks]
    return jsonify({
        'success': True,
        'drinks': drinks_formatted
        })

# TODO DONE implement endpoint /drinks-detail
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    drinks = Drink.query.all()
    drinks_formatted = [drinks.long() for drinks in drinks]

    return jsonify({
        'success': True,
        'drinks': drinks_formatted
        })

# TODO-DONE implement endpoint POST /drinks
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()
    title = body.get('title', None)
    recipe = str(json.dumps(body.get('recipe', None)))
    new_drink = Drink(title=title, recipe=recipe)
    new_drink.insert()
    drinks = []
    drinks.append(new_drink.long())
    return jsonify({
        'success': True,
        'drinks': drinks
        })


# TODO DONE implement endpoint PATCH /drinks/<id>
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    """Updates existing drink and returns it to client"""
    # Get body from request
    body = request.get_json()
    if not body:
        abort(400, {'message': 'request does not contain a valid JSON body.'})
    # Find drink which should be updated by id
    drink_to_update = Drink.query.filter(Drink.id == drink_id).one_or_none()
    # Check if and which fields should be updated
    updated_title = body.get('title', None)
    updated_recipe = body.get('recipe', None)
    # Depending on which fields are available, make apropiate updates
    if updated_title:
        drink_to_update.title = body['title']
    if updated_recipe:
        drink_to_update.recipe = """{}""".format(body['recipe'])
    drink_to_update.update()
    return jsonify({
        'success': True,
        'drinks': [Drink.long(drink_to_update)]
        })

# TODO DONE implement endpoint DELETE /drinks/<drink_id>
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    drink = Drink.query.get(drink_id)

    if drink is None:
        abort(404)
    else:
        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
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

@app.errorhandler(401)
def custom_401(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized user, please login and try again."
        }), 401

@app.errorhandler(AuthError)
def handle_auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error.code
        }), error.status_code
