from flask import jsonify, make_response, render_template, request
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_restful import Resource
from config import app, api

# Home Resource
class HomeResource(Resource):
    def get(self):
        return make_response(jsonify({'message': 'Welcome to the API'}), 200)
api.add_resource(HomeResource, '/api')