"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        user_1 = User.signup('user1', 'user1@email.com', 'password1', 'None')
        user_1.id = 999

        db.session.commit()

        user_1 = User.query.get(user_1.id)

        self.user_1 = user_1
        self.user_1_id = user_1.id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """test message model"""

        msg = Message(
            text="hello warble",
            user_id = self.user_1_id
        )
        db.session.add(msg)
        db.session.commit()

        self.assertEqual(len(self.user_1.messages), 1)
        self.assertEqual(self.user_1.messages[0].text, "hello warble")

    def test_message_likes(self):
        msg1 = Message(
            text="hello warble",
            user_id = self.user_1_id
        )
        msg2 = Message(
            text="cool",
            user_id = self.user_1_id
        )       

        user = User.signup('user', 'user@email.com', 'password', None)
        user.id = 5555555
        db.session.add_all([msg1, msg2, user])
        db.session.commit()

        user.likes.append(msg1)
        db.session.commit()

        #get all user likes by filtering like's user id that is same as user's
        user_likes = Likes.query.filter(Likes.user_id == user.id).all()
        self.assertEqual(len(user_likes), 1)
        self.assertEqual(user_likes[0].message_id, msg1.id)
