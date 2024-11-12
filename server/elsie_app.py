from flask import jsonify, make_response, request
from flask_restful import Resource
from config import app, api, db
from models import Category,Post
from sqlalchemy.exc import SQLAlchemyError

# Home Resource
class HomeResource(Resource):
    def get(self):
        return make_response(jsonify({"message": "Welcome to the API"}), 200)

class CategoryResource(Resource):
    def post(self):
        data = request.json
        name = data.get("name")
        description = data.get("description")
        
        if not name:
            return make_response(jsonify({"error": "Category name is required"}), 400)
        
        new_category = Category(name=name, description=description)
        db.session.add(new_category)
        db.session.commit()
        
        return make_response(jsonify({
            "message": "Category created",
            "category": {"name": name, "description": description}
        }), 201)
    
class ApprovePost(Resource):
    def put(self, post_id):
        post = Post.query.get(post_id)
        if not post:
            return {"error": "Post not found"}, 404

        if post.approved:
            return {"message": "Post is already approved"}, 200

        try:
            post.approved = True
            db.session.commit()
            return {"message": f"Post {post_id} approved"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Failed to approve post", "details": str(e)}, 500

class FlagPost(Resource):
    def post(self, post_id):
        post = Post.query.get(post_id)
        if not post:
            return make_response(jsonify({"error": "Post not found"}), 404)

        data = request.json
        post.flagged = True

        # Commit changes to the database
        db.session.commit()

        return jsonify({
            "message": "Post flagged",
        }), 200
class EditPost(Resource):
    def put(self, post_id):
        post = Post.query.get(post_id)
        if not post:
            return {"error": "Post not found"}, 404
        
        data = request.json
        # Conditional updates only if values are different
        if 'title' in data and data['title'] != post.title:
            post.title = data['title']
        if 'body' in data and data['body'] != post.body:
            post.body = data['body']
        if 'post_type' in data and data['post_type'] != post.post_type:
            post.post_type = data['post_type']
        if 'thumbnail_url' in data and data['thumbnail_url'] != post.thumbnail_url:
            post.thumbnail_url = data['thumbnail_url']
        if 'likes_count' in data and data['likes_count'] != post.likes_count:
            post.likes_count = data['likes_count']
        if 'approved' in data and data['approved'] != post.approved:
            post.approved = data['approved']
        
        if db.session.is_modified(post):
            post.updated_at = db.func.now()
            db.session.commit()
            message = f"Post {post_id} updated successfully"
        else:
            message = "No changes made to the post"

        return {
            "message": message,
            "post": {
                "id": post.id,
                "title": post.title,
                "body": post.body,
                "post_type": post.post_type,
                "thumbnail_url": post.thumbnail_url,
                "likes_count": post.likes_count,
                "approved": post.approved,
                "updated_at": post.updated_at.strftime('%Y-%m-%d %H:%M:%S') if post.updated_at else None
            }
        }, 200



# Adding resources to the API
api.add_resource(HomeResource, "/api")
api.add_resource(CategoryResource, '/api/categories')
api.add_resource(ApprovePost, '/api/posts/<int:post_id>/approve')
api.add_resource(FlagPost, '/api/posts/<int:post_id>/flag')
api.add_resource(EditPost, '/api/posts/<int:post_id>/edit')


if __name__ == "__main__":
    app.run(port=5555, debug=True)