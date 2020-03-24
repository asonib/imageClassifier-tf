from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
app = Flask(__name__)

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
def checkUser(username):

    client = MongoClient('localhost://27017')
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

        checkUser = checkUser(username)
        if checkUser != 200:
            retJson = {
                'status code': 302,
                'message': 'username taken'
            }
            return jsonify(retJson)
        
        client = MongoClient('mongodb://27017')
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

if __name__ == '__main__':
    app.run()