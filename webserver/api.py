from flask import Flask
from flask_restful import Resource, Api
from flask import request

app = Flask(__name__)
api = Api(app)

class Product(Resource):
    def get(self):
        sentence = request.form['sentence']
        return {
            'test': ['test1', 'test2', 'test3']
        }

api.add_resource(Product, '/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)