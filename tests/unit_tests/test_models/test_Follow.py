from datetime import datetime
from .base import ModelTest
from app import db
from app.models import User, Follow


def create_u1_u2():
	u1 = User(email='john@example.com', password='cat')
	u2 = User(email='susan@example.org', password='dog')
	db.session.add(u1)
	db.session.add(u2)
	db.session.commit()
	return u1, u2


class UserModelTest(ModelTest):

	def test_follow_not_self_created(self):
		u1, u2 = create_u1_u2()
		self.assertFalse(u1.is_following(u2))
		self.assertFalse(u2.is_followed_by(u1))
		self.assertFalse(u2.is_following(u1))
		self.assertFalse(u1.is_followed_by(u2))

	def test_is_following_and_is_followed_by(self):
		u1, u2 = create_u1_u2()
		u1.follow(u2)
		self.assertTrue(u1.is_following(u2))
		self.assertFalse(u1.is_followed_by(u2))
		self.assertFalse(u2.is_following(u1))
		self.assertTrue(u2.is_followed_by(u1))

	def test_follow_timestamp_is_correct(self):
		u1, u2 = create_u1_u2()
		timestamp_before = datetime.utcnow()
		u1.follow(u2)
		timestamp_after = datetime.utcnow()
		f = Follow.query.filter_by(follower=u1, followed=u2).first()
		self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)

	def test_followed_and_followers_count(self):
		u1, u2 = create_u1_u2()
		u1.follow(u2)
		self.assertTrue(u1.followed.count() == 2)
		self.assertTrue(u2.followers.count() == 2)

	def test_Follow_match_followers_and_followed(self):
		u1, u2 = create_u1_u2()
		u1.follow(u2)
		f = u1.followed.all()[-1]
		self.assertTrue(f.followed == u2)
		f = u2.followers.all()[-1]
		self.assertTrue(f.follower == u1)
	
	def test_unfollow_deletes_Follow(self):
		u1, u2 = create_u1_u2()
		u1.follow(u2)
		u1.unfollow(u2)
		self.assertTrue(u1.followed.count() == 1)
		self.assertTrue(u2.followers.count() == 1)
		self.assertTrue(Follow.query.count() == 2)
		
	def test_Follow_not_exist_after_follower_deleted(self):
		u1, u2 = create_u1_u2()
		u1.follow(u2)
		db.session.delete(u1)
		db.session.commit()
		self.assertTrue(Follow.query.count() == 1)

	def test_Follow_not_exist_after_followed_deleted(self):
		u1, u2 = create_u1_u2()
		u1.follow(u2)
		db.session.delete(u2)
		db.session.commit()
		self.assertTrue(Follow.query.count() == 1)