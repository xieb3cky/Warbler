"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc


from models import db, User, Message, Follows

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        user_1 = User.signup('user1', 'user1@email.com', 'password1', 'None')
        user_1.id = 999

        user_2 = User.signup('user2', 'user2@email.com', 'password2', 'None')
        user_2.id = 666

        db.session.commit()

        user_1 = User.query.get(user_1.id)
        uuser2 = User.query.get(user_2.id)

        self.user_1 = user_1
        self.user_1_id = user_1.id

        self.user_2 = user_2
        self.user_2_id = user_2.id
        
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

####
#test following & follower methods
####

    def test_user_follows(self):

        #add user#1 as user#2's follower
        self.user_1.following.append(self.user_2)
        db.session.commit()

        #user1:
        #follower: 0
        #following: 1

        #user2: 
        #follower: 1
        #following: 0
        self.assertEqual(len(self.user_1.following),1)
        self.assertEqual(len(self.user_1.followers),0)
        self.assertEqual(len(self.user_2.following),0)
        self.assertEqual(len(self.user_2.followers),1)

        #user_1 following[0]'s id should be user_2.id
        self.assertEqual(self.user_1.following[0].id, self.user_2.id)
        #user_2 follower[0]'s id should be user_1.id
        self.assertEqual(self.user_2.followers[0].id, self.user_1.id)

    def test_is_following(self):
        """test is_following method""" 

        #add user#1 as user#2's follower
        self.user_1.following.append(self.user_2)
        db.session.commit()

        self.assertTrue(self.user_1.is_following(self.user_2))
        self.assertFalse(self.user_2.is_following(self.user_1))

    def test_is_followed_by(self):
        """test is_followed_by method""" 
        
        #add user#1 as user#2's follower
        self.user_1.following.append(self.user_2)
        db.session.commit()

        self.assertTrue(self.user_2.is_followed_by(self.user_1))
        self.assertFalse(self.user_1.is_followed_by(self.user_2))
    

####
#test signup 
####  
    def test_valid_signup(self):
        """ test User.create successfully creates a new user given valid credentials"""
        test_user = User.signup("test_username", "test@email.com", "password", None)
        test_user.id = 444
        db.session.commit()

        test_user = User.query.get(test_user.id) 
        self.assertEqual(test_user.username, "test_username")
        self.assertEqual(test_user.email,"test@email.com")
        self.assertNotEqual(test_user.password,"test@email.com", "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(test_user.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        """test User.create fail to create new user if any of the validation fails"""
        test_user = User.signup(None, "test@email.com", "password", None)
        test_user.id = 56789
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        test_user = User.signup("tester",None, "password", None)
        test_user.id = 1234789
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testing","testing@email.com", "", None)
        with self.assertRaises(ValueError) as context:
            User.signup("testing","testing@email.com", None, None)

    def test_valid_auth(self):
        """test User.authetnicate successfully return a user when given valid username & password"""
        test_user = User.authenticate(self.user_1.username, "password1")
        self.assertIsNotNone(test_user)
        self.assertEqual(test_user.id, self.user_1.id)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("bad_username", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.user_1.username, "bad_password"))

