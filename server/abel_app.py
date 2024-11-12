from flask import jsonify, make_response, render_template, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, get_jwt_identity, jwt_required
from flask_restful import Resource, reqparse
from config import app, api, db, jwt
from models import User, Post, Comment, Subscription, Like, Notification, Category

# Blacklist check for both access and refresh tokens
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload['jti'] in app.config['BLACKLIST']

# Home Resource
class HomeResource(Resource):
    def get(self):
        return make_response(jsonify({"message": "Welcome to the API"}), 200)

# Signup Resource
class SignupResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help='Username is required')
        parser.add_argument('email', required=True, help='Email is required')
        parser.add_argument('password', required=True, help='Password is required')
        data = parser.parse_args()

        # Check if user exists by email
        if User.query.filter_by(email=data['email']).first():
            return {"message": "User with this email already exists"}, 400
        
        # Create a new user
        new_user = User(username=data['username'], email=data['email'])

        # Hashing handled by the password setter
        new_user.password = data['password']
        db.session.add(new_user)
        db.session.commit()

        return {"message": "User created successfully"}, 201
    
# Login Resource
class LoginResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help='Email is required')
        parser.add_argument('password', required=True, help='Password is required')
        data = parser.parse_args()

        # Find user by email
        user = User.query.filter_by(email=data['email']).first()

        # Authenticate user
        if not user or not user.authenticate(data['password']):
            return {"message": "Invalid credentials"}, 401
        
        # Create JWT token
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200

# Refresh Token Resource
class RefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return {'access_token': access_token }, 200
    
# Logout Resource
class LogoutResource(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        app.config['BLACKLIST'].add(jti)
        return {"message": "Logged out successfully"}, 200
        

api.add_resource(HomeResource, "/api")
api.add_resource(SignupResource, "/api/signup")
api.add_resource(LoginResource, "/api/login")
api.add_resource(RefreshResource,  "/api/refresh")
api.add_resource(LogoutResource, "/api/logout")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
