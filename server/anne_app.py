from flask import jsonify, make_response, request
from flask_restful import Resource
from config import app, api, db
from models import  Subscription, Like, Notification, Category

# Home Resource
class HomeResource(Resource):
    def get(self):
        return make_response(jsonify({"message": "Welcome to the API"}), 200)

class Subscribe(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        category_id = data.get('category_id')

        if not user_id or not category_id:
            return {"error": "user_id and category_id are required"}, 400

        # Check if the subscription already exists
        existing_subscription = Subscription.query.filter_by(user_id=user_id, category_id=category_id).first()
        if existing_subscription:
            return {"message": "Already subscribed to this category"}, 200

        # Create a new subscription
        subscription = Subscription(user_id=user_id, category_id=category_id)
        db.session.add(subscription)
        db.session.commit()
        
        # Return the new subscription as a dictionary
        return {
            "id": subscription.id,
            "user_id": subscription.user_id,
            "category_id": subscription.category_id
        }, 201

class Unsubscribe(Resource):
    def delete(self):
        data = request.get_json()
        user_id = data.get('user_id')
        category_id = data.get('category_id')

        subscription = Subscription.query.filter_by(user_id=user_id, category_id=category_id).first()
        if not subscription:
            return ({"error": "Subscription not found"}), 404

        db.session.delete(subscription)
        db.session.commit()
        
        return ({"message": "Unsubscribed successfully"}), 200

class AddToWishlist(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        post_id = data.get('post_id')

        if not user_id or not post_id:
            return jsonify({"error": "user_id and post_id are required"}), 400

        # Check if the item is already in the user's wishlist
        existing_wishlist_item = Wishlist.query.filter_by(user_id=user_id, post_id=post_id).first()
        if existing_wishlist_item:
            return jsonify({"message": "Item is already in the wishlist"}), 200

        # Add item to wishlist
        wishlist_item = Wishlist(user_id=user_id, post_id=post_id)
        db.session.add(wishlist_item)
        db.session.commit()

        return jsonify(wishlist_item.to_dict()), 201

class RemoveFromWishlist(Resource):
    def delete(self):
        data = request.get_json()
        user_id = data.get('user_id')
        post_id = data.get('post_id')

        wishlist_item = Wishlist.query.filter_by(user_id=user_id, post_id=post_id).first()
        if not wishlist_item:
            return jsonify({"error": "Item not found in wishlist"}), 404

        db.session.delete(wishlist_item)
        db.session.commit()

        return jsonify({"message": "Item removed from wishlist"}), 200


class GetNotifications(Resource):
    def get(self, user_id):
        notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
        return [
            {
                "id": notification.id,
                "user_id": notification.user_id,
                "message": notification.message,
                "created_at": notification.created_at.isoformat()
            } for notification in notifications
        ], 200


api.add_resource(HomeResource, "/api")
api.add_resource(Subscribe, '/api/subscribe')
api.add_resource(Unsubscribe, '/api/unsubscribe')
api.add_resource(AddToWishlist, '/api/wishlist/add')
api.add_resource(RemoveFromWishlist, '/api/wishlist/remove')
api.add_resource(GetNotifications, '/api/notifications/<int:user_id>')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
