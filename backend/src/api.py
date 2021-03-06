import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    return jsonify({
      'success': True,
      'drinks': [drink.short() for drink in drinks]
    })



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    drinks = Drink.query.all()
    return jsonify({
      'success': True,
      'drinks': [drink.long() for drink in drinks]
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    body = request.get_json()
    drink = Drink()
    drink.title = body['title']
    drink.recipe = json.dumps(body['recipe'])
    print(drink.title, file=sys.stderr)
    print(drink.recipe, file=sys.stderr)
    try:
        drink.insert()
        return jsonify({
            'success': True,
            'drinks': drink.long()
        })
    except Exception as e:
        print(e)
        abort(422)
    
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    body = request.get_json()
    drink_to_update = Drink.query.filter(Drink.id == drink_id).one_or_none()

    #if not existing - 404 error
    if drink_to_update is None:
        abort(404)
    
    # check if title or receipe has changed, otherwise keep old one
    try:
        drink_to_update.title= body['title'] 
    except: 
        drink_to_update.title = drink_to_update.title
    try:
        drink_to_update.recipe= body['receipe'] 
    except: 
        drink_to_update.recipe = drink_to_update.recipe
   
    #print(drink_to_update.title, file=sys.stderr)
    #print(drink_to_update.recipe, file=sys.stderr)
    try:
        drink_to_update.update()
        return jsonify({
            'success': True,
            'drinks': [drink_to_update.long()],
        })
    except Exception as e:
        print(e)
        abort(422)
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    try:
        drink_to_delete = Drink.query.filter(Drink.id == drink_id).one_or_none()

        #if not existing - 404 error
        if drink_to_delete is None:
            abort(404)
        #delete from db

        drink_to_delete.delete()

        return jsonify({
            'success': True,
            'delete': drink_id,
        })
    except Exception as e:
        print(e)
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

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
                    "success": False, 
                    "error": 500,
                    "message": "Internal server error"
                    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
