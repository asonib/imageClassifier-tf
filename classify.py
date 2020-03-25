from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import config

app = Flask(__name__)
key = config.config["Password"]

api = Api(app)

@app.route('/')
def helloFlask():
    print('Hello Flask')
    return '<h1>Flask Server</h1>'

def checkPostedData(postedData, route):
    if route == 'register':
        if 'Username' not in postedData or 'Password' not in postedData:
            return 301
        else:
            return 200
    elif route == 'login':
        if 'Username' not in postedData or 'Password' not in postedData:
            return 301
        else:
            return 200
def checkUsers(username):
    client = MongoClient('mongodb+srv://asonib:{}@classifier-htisx.mongodb.net/test?retryWrites=true&w=majority'.format(key))
    db = client.ImageClassification
    users = db['Users']
    if users.find({'Username': username}).count() == 1:
        return 302
    else:
        return 200


class Register(Resource):
    def post(self):
        postedData = request.get_json()
        checkData = checkPostedData(postedData, 'register')
        if checkData != 200:
            retJson = {
                'status code':301,
                'message': 'missing Data'
            }
            return jsonify(retJson)
        username = postedData['Username']
        password = postedData['Password']

        checkUser = checkUsers(username)
        if checkUser != 200:
            retJson = {
                'status code': 302,
                'message': 'username taken'
            }
            return jsonify(retJson)
        
        client = MongoClient('mongodb+srv://asonib:{}@classifier-htisx.mongodb.net/test?retryWrites=true&w=majority'.format(key))
        db = client.ImageClassification
        users = db['Users']

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        users.insert({'Username': username, 'Password': hashed_pw, 'Tokens': 25})

        retJson = {
            'status code': 200,
            'message': 'user registered'
        }
        return jsonify(retJson)
api.add_resource(Register, '/register')

def checkLogin(username, password):
    client = MongoClient('mongodb+srv://asonib:{}@classifier-htisx.mongodb.net/test?retryWrites=true&w=majority'.format(key))
    db = client.ImageClassification
    users = db['Users']

    if users.find({'Username': username}).count() == 0:
        return 302
    hashed_pw = users.find({'Username': username})[0]['Password']
    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) != hashed_pw:
        return 303
    else:
        tokens = users.find({'Username': username})[0]['Tokens']
        if tokens < 0:
            return 304
        tokens -= 1
        users.update({'Username': username}, {'$set': {'Tokens':tokens}})
        return 200

class Login(Resource):
    def post(self):
        postedData = request.get_json()
        checkData = checkPostedData(postedData, 'login')
        if checkData != 200:
            retJson = {
                'status code': 301,
                'message': 'missing data'
            }
            return jsonify(retJson)
        username = postedData['Username']
        password = postedData['Password']
        credintials = checkLogin(username, password)
        if credintials == 302:
            retJson = {
                'status code': 302,
                'message': 'user does not exist'
            }
            return jsonify(retJson)
        if credintials == 303:
            retJson = {
                'status code': 303,
                'message': 'incorrect password'
            }
            return jsonify(retJson)
        if credintials == 304:
            retJson = {
                'status code': 304,
                'message': 'out of tokens'
            }
            return jsonify(retJson)
        retJson = {
            'status code': 200,
            'message': 'Logged In'
        }
        return jsonify(retJson)
api.add_resource(Login, '/login')

if __name__ == '__main__':
    app.run()