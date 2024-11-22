from datetime import datetime
from sqlalchemy import text
from models import Comment, User, Post
from config import app, db

def clear_comments_table():
    # Clear existing comments
    db.session.query(Comment).delete()
    db.session.commit()
    print("Comments table cleared.")

    # Reset the ID sequence to start from 1
    db.session.execute(text("ALTER SEQUENCE comments_id_seq RESTART WITH 1"))
    db.session.commit()

# Function to seed comments
def seed_comments_table():
    with app.app_context():
        try:
            # clear_comments_table()

            # Create parent comments first for each post
            parent_comments = [
                Comment(post_id=1, user_id=1, body="Wow, this topic is really engaging! I can't wait to see more posts like this.", created_at=datetime.now()),
                Comment(post_id=1, user_id=2, body="The analysis here is quite insightful. I'll definitely share this with my network.", created_at=datetime.now()),
                Comment(post_id=1, user_id=3, body="Here's a different perspective: This could be more interactive for readers.", created_at=datetime.now()),

                Comment(post_id=2, user_id=2, body="This really made me think deeper. A very refreshing perspective.", created_at=datetime.now()),
                Comment(post_id=2, user_id=7, body="I appreciate how clear the examples were. It really made the concept much easier to understand.", created_at=datetime.now()),
                Comment(post_id=2, user_id=4, body="Do you mind clarifying the point about X? I feel like I missed something.", created_at=datetime.now()),

                Comment(post_id=3, user_id=3, body="I think the main point of this post could have been expanded further, but overall it’s solid!", created_at=datetime.now()),
                Comment(post_id=3, user_id=4, body="There were a few confusing sections, but I understand the core idea now.", created_at=datetime.now()),
                Comment(post_id=3, user_id=5, body="This is incredibly helpful. I’m going to revisit this post for sure.", created_at=datetime.now()),

                Comment(post_id=4, user_id=1, body="This post really challenges my thinking in a good way. A lot to consider.", created_at=datetime.now()),
                Comment(post_id=4, user_id=7, body="I hadn’t thought about it from that angle before. Excellent read!", created_at=datetime.now()),
                Comment(post_id=4, user_id=3, body="This provides a new lens through which to view the issue. Great work.", created_at=datetime.now()),

                Comment(post_id=5, user_id=6, body="At first, this felt overwhelming, but after rereading, it clicked.", created_at=datetime.now()),
                Comment(post_id=5, user_id=2, body="I had the same issue! But the examples cleared up my confusion.", created_at=datetime.now()),
                Comment(post_id=5, user_id=4, body="I really appreciate how this was broken down. The structure makes sense now.", created_at=datetime.now()),

                Comment(post_id=6, user_id=6, body="At first, I didn’t understand the idea, but after thinking about it, it makes sense now.", created_at=datetime.now()),
                Comment(post_id=6, user_id=1, body="This article really helped me see things in a new light. Great job!", created_at=datetime.now())
            ]

            # Add parent comments to the session
            for comment in parent_comments:
                db.session.add(comment)

            # Commit to generate IDs for the parent comments
            db.session.commit()

            # Now add replies using the generated IDs of parent comments
            replies = [
                # Replies for post 1
                Comment(post_id=1, user_id=4, body="Absolutely! I'd love to see more in-depth discussions like this.", created_at=datetime.now(), parent_comment_id=parent_comments[0].id),
                Comment(post_id=1, user_id=5, body="I agree, it’s a fantastic take. Looking forward to more content!", created_at=datetime.now(), parent_comment_id=parent_comments[1].id),
                Comment(post_id=1, user_id=6, body="Could you elaborate more on the point about X? I’d like to hear more!", created_at=datetime.now(), parent_comment_id=parent_comments[2].id),

                # Replies for post 2
                Comment(post_id=2, user_id=5, body="Glad you found it helpful! I agree, it was eye-opening.", created_at=datetime.now(), parent_comment_id=parent_comments[3].id),
                Comment(post_id=2, user_id=6, body="Here’s the additional clarification you asked for.", created_at=datetime.now(), parent_comment_id=parent_comments[5].id),

                # Replies for post 3
                Comment(post_id=3, user_id=6, body="Yeah, I felt the same way! After rereading it, it makes sense.", created_at=datetime.now(), parent_comment_id=parent_comments[6].id),
                Comment(post_id=3, user_id=1, body="Exactly! I'm glad you found it useful. Let me know if you have any other questions.", created_at=datetime.now(), parent_comment_id=parent_comments[7].id),

                # Replies for post 4
                Comment(post_id=4, user_id=4, body="I had the same reaction! It’s definitely challenging, but worth considering.", created_at=datetime.now(), parent_comment_id=parent_comments[9].id),
                Comment(post_id=4, user_id=5, body="Yeah, it’s a bit of a shift in perspective, but it makes total sense.", created_at=datetime.now(), parent_comment_id=parent_comments[10].id),

                # Replies for post 5
                Comment(post_id=5, user_id=3, body="This gave me a clear starting point to dive deeper into the topic. Thanks!", created_at=datetime.now(), parent_comment_id=parent_comments[12].id),
                Comment(post_id=5, user_id=5, body="Exactly! The examples made the abstract concepts much clearer.", created_at=datetime.now(), parent_comment_id=parent_comments[13].id),

                # Replies for post 6
                Comment(post_id=6, user_id=2, body="Glad it helped! I had a similar experience.", created_at=datetime.now(), parent_comment_id=parent_comments[14].id),
                Comment(post_id=6, user_id=3, body="This helped me a lot too. Thank you for the great breakdown.", created_at=datetime.now(), parent_comment_id=parent_comments[15].id)
            ]

            # Add replies to the session
            for reply in replies:
                db.session.add(reply)

            # Commit all changes
            db.session.commit()
            print("Seeded comments successfully.")

        except Exception as e:
            # Rollback if any error occurs
            db.session.rollback()
            print("Error seeding comments:", str(e))

# Run the seed function
if __name__ == "__main__":
    seed_comments_table()
