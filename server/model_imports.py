def get_models():
    from user_model import User
    from post_model import Post
    from notification_model import Notification
    from comment_model import Comment
    from like_model import Like
    from subscription_model import Subscription
    from category_model import Category

    return User, Post, Notification, Comment, Like, Subscription, Category