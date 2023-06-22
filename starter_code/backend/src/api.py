import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, get_token_auth_header

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def drinks():
    try:
        drinks = Drink.query.all()
        # drink_instace = Drink()
        # drinks = drink_instace.short()
        return jsonify({
            "success": True,
            "drinks" : [d.short() for d in drinks]
        }), 200
    except:
        abort(404, description="Drinks not found")

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    try:
        drinks = Drink.query.all()
        return jsonify({
            "success" : True,
            "drinks" : [d.long() for d in drinks]
        }), 200
    except:
        abort(422)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods = ['POST'])
@requires_auth('post:drinks')
def new_drink(payload):
    req =  request.get_json()
    try:
        request_recipe = req['recipe']
        #If the recipe has a single ingridient the return would be a instance, so we need to convert it to a list
        if isinstance(request_recipe, dict):
            request_recipe = [request_recipe]
        
        new_drink = Drink()
        new_drink.title = req['title']
        new_drink.recipe = json.dumps(request_recipe)  # convert object to a string
        new_drink.insert()
        
    except BaseException as e:
        print(e)
        abort(400)
        
    return jsonify({
        "success" : True,
        "drinks" : [new_drink.long()]
    })

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
@app.route('/drinks/<id>', methods = ['PATCH'])
@requires_auth('patch:drinks')
def edit_drinks(payload, id):
    req = request.get_json()
    drink = Drink.query.filter_by(id = id).one_or_none()
    
    if not drink:
        abort(404)
    
    try:
        if req.get('title'):
            drink.title = req.get('title')
        if req.get('recipe'):
            drink.recipe = json.dumps(req.get('recipe'))
        drink.update()
    except BaseException as e:
        abort(400)
    
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    }), 200
    

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

@app.route('/drinks/<id>', methods = ['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    drink = Drink.query.filter_by(id=id).one_or_none()
    
    if not drink:
        abort(404)
    
    try:
        drink.delete()
    except:
        abort(400)
    
    return jsonify({
        "success": True,
        "delete": id
    }), 200

# Error Handling
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
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404
    
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405

# Default port:
if __name__ == '__main__':
    app.run()
