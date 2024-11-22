from seed_category import seed_categories_table, clear_categories_table
from seed_user import seed_users_table, clear_users_table
from seed_post import seed_posts_table, clear_posts_table
from seed_subscription import seed_subscriptions_table, clear_subscriptions_table
from seed_comment import seed_comments_table, clear_comments_table
from seed_like import seed_likes_table, clear_likes_table
from seed_notification import seed_notifications_table, clear_notifications_table
from seed_wishlist import seed_wishlist_table, clear_wishlist_table
from config import app

def seed_all_tables():
    with app.app_context():
        try:
            # Clear all tables in reverse order of dependencies
            clear_likes_table()
            clear_comments_table()
            clear_subscriptions_table()
            clear_posts_table()
            clear_notifications_table()
            clear_users_table()
            clear_wishlist_table()
            clear_categories_table()

            # Seed tables in order of no dependencies
            seed_categories_table()
            seed_users_table()
            seed_posts_table()
            seed_wishlist_table()
            seed_subscriptions_table()
            seed_comments_table()
            seed_likes_table()
            seed_notifications_table()

            print("All tables seeded successfully.")

        except Exception as e:
            print(f"Error seeding all tables {e}")

if __name__ == "__main__":
    seed_all_tables()